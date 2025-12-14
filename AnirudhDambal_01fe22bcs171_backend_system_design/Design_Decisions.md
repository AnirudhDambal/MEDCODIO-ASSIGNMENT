# Design Decisions & Architecture Explanation

## Table of Contents
1. [Multi-Tenancy Approach](#multi-tenancy-approach)
2. [Database Design Decisions](#database-design-decisions)
3. [API Design Decisions](#api-design-decisions)
4. [Versioning Strategy](#versioning-strategy)
5. [Security & Privacy](#security--privacy)
6. [Scalability Considerations](#scalability-considerations)
7. [Future Extensibility](#future-extensibility)

---

## Multi-Tenancy Approach

### Design Choice: Organization-Based Row-Level Isolation

**Decision**: Implement multi-tenancy at the database level with `organization_id` as a foreign key on all tenant-scoped tables.

**Rationale**:
1. **Data Isolation**: Each organization's data is completely isolated, preventing accidental cross-tenant data access
2. **Query Simplicity**: All queries naturally include `organization_id`, making isolation explicit in the code
3. **Performance**: Indexes on `organization_id` ensure efficient filtering
4. **Compliance**: Meets healthcare data privacy requirements (HIPAA) by ensuring data segregation

**Implementation**:
- All tenant-scoped tables (providers, patients, encounters) include `organization_id`
- Composite unique constraints include `organization_id` (e.g., `patient_mrn` is unique per organization)
- Application middleware extracts `organization_id` from authenticated user context
- Optional: Row-Level Security (RLS) policies in PostgreSQL for defense-in-depth

**Alternative Considered**: Separate databases per tenant
- **Rejected**: More complex infrastructure, harder to manage, not scalable for thousands of tenants

---

## Database Design Decisions

### 1. UUID vs. Auto-Incrementing Integers

**Decision**: Use UUID primary keys for all entities.

**Rationale**:
- **Security**: UUIDs are non-sequential, preventing enumeration attacks
- **Distributed Systems**: No coordination needed across database instances
- **Global Uniqueness**: UUIDs work across databases without conflicts
- **Privacy**: No information leakage about data volume or creation order

**Trade-off**: Slightly larger storage (16 bytes vs 8 bytes) and slightly slower index lookups, but benefits outweigh costs.

---

### 2. Soft Deletes vs. Hard Deletes

**Decision**: Implement soft deletes using `deleted_at` timestamp column.

**Rationale**:
- **Audit Trail**: Preserve data for compliance and auditing requirements
- **Data Recovery**: Can recover accidentally deleted records
- **Referential Integrity**: Maintain relationships while allowing logical deletion
- **Audit Requirements**: Healthcare regulations require data retention

**Implementation**:
- All queries exclude soft-deleted records: `WHERE deleted_at IS NULL`
- Partial indexes optimize queries on active records
- Historical data can be archived separately if needed

---

### 3. Separate Tables for ICD and CPT Codes

**Decision**: Use separate `icd_codes` and `cpt_codes` tables instead of a unified `medical_codes` table.

**Rationale**:
- **Different Attributes**: ICD codes have different metadata than CPT codes
- **Query Performance**: Separate tables allow optimized indexes for each code type
- **Type Safety**: Application logic can enforce type-specific validations
- **Maintenance**: Easier to update code sets independently

**Alternative Considered**: Single polymorphic table with type discriminator
- **Rejected**: More complex queries, type-specific fields would be nullable, less clear schema

---

### 4. Assignment Tables for Encounter-Code Relationships

**Decision**: Create separate `encounter_icd_assignments` and `encounter_cpt_assignments` tables (junction tables).

**Rationale**:
- **Many-to-Many Relationship**: Encounters can have multiple codes, codes can appear in multiple encounters
- **Rich Metadata**: Assignment tables store encounter-specific information:
  - Assignment type (primary/secondary for ICD)
  - Quantity and modifiers (for CPT)
  - Confidence scores from NLP
  - Assignment timestamps and users
- **Audit Trail**: Track changes to code assignments over time
- **Flexibility**: Support multiple versions of code assignments

**Alternative Considered**: Store codes as JSON arrays in encounters table
- **Rejected**: Cannot query efficiently, no referential integrity, harder to audit changes

---

### 4.1. Modifier Rule Design

**Decision**: Create separate `cpt_modifier_rules` table to define valid modifier-procedure combinations.

**Rationale**:
- **Business Rules**: Not all modifiers are valid for all CPT codes (e.g., bilateral modifier not valid for colonoscopy)
- **Validation**: API can validate modifier assignments before saving
- **Compliance**: Ensures billing accuracy by preventing invalid modifier combinations
- **Flexibility**: Rules can change over time (effective dates)
- **Data Integrity**: Prevents invalid modifier assignments at database level

**Implementation**:
- `cpt_modifier_rules` table links CPT codes to allowed modifiers
- Supports effective dates for rule changes
- Can explicitly mark modifiers as disallowed
- API endpoint to query valid modifiers for a CPT code
- Validation endpoint to check modifier validity

**Example Rules**:
- CPT 45378 (Colonoscopy) → Allowed: 25, 59, LT, RT → Disallowed: 50 (bilateral)
- CPT 99213 (Office visit) → Allowed: 25, 57 → Disallowed: 59, 76, 77

---

### 5. Code Versioning Approach

**Decision**: Include `code_version` column in code tables, with unique constraint on `(code, code_version)`.

**Rationale**:
- **Historical Accuracy**: Maintain historical code sets (ICD-10 updates annually)
- **Compliance**: Ensure codes used in past encounters remain valid for billing
- **Query Flexibility**: Can search latest codes or historical versions
- **Backward Compatibility**: Old encounters retain their original code versions

**Implementation**:
- Default to latest version in API queries
- Assignment tables reference code by ID (which includes version)
- Code search allows version filtering

**Alternative Considered**: Create new code entries with version suffix
- **Rejected**: Would create duplicate code entries, harder to track changes

---

### 6. Audit Trail Design

**Decision**: Separate `code_assignment_history` table for tracking all code assignment changes.

**Rationale**:
- **Compliance**: Healthcare regulations require audit trails for billing codes
- **Debuggability**: Track how and why codes were changed
- **Analytics**: Analyze coding patterns and accuracy over time
- **Non-Intrusive**: Doesn't pollute main assignment tables with history

**Implementation**:
- Store old and new values as JSONB for flexibility
- Track action type (created, updated, deleted, confirmed)
- Include user ID and timestamp for accountability
- Can be queried independently or joined with assignments

---

### 7. Indexing Strategy

**Decision**: Comprehensive indexing with partial indexes for soft-deleted records.

**Key Indexes**:
- Primary keys (automatic)
- Foreign keys for joins
- Composite indexes for common query patterns
- Partial indexes excluding soft-deleted records: `WHERE deleted_at IS NULL`
- Full-text search indexes (GIN) on code descriptions

**Rationale**:
- **Query Performance**: Fast lookups on frequently queried columns
- **Multi-Tenancy**: Indexes on `organization_id` ensure tenant isolation queries are fast
- **Partial Indexes**: Reduce index size by excluding deleted records
- **Full-Text Search**: Enable fast code search by description

---

## API Design Decisions

### 1. RESTful Resource Naming

**Decision**: Use hierarchical resource paths reflecting organizational structure.

**Pattern**: `/organizations/{org_id}/resource/{resource_id}`

**Rationale**:
- **Multi-Tenancy**: Organization ID in path makes tenant scope explicit
- **Intuitive**: Reflects real-world hierarchy (org → provider → patient → encounter)
- **Security**: Path parameter ensures user can only access their organization's data
- **REST Compliance**: Follows REST principles with clear resource relationships

**Example**: 
```
GET /organizations/{org_id}/patients/{patient_id}/encounters
```

---

### 2. Nested Resources vs. Flat Endpoints

**Decision**: Mix of nested and flat endpoints based on use case.

**Nested**: 
- Organization-scoped resources (providers, patients, encounters)
- Encounter-scoped code assignments

**Flat**:
- Medical codes (shared across all organizations)
- Code search (no tenant scope needed)

**Rationale**:
- **Nested**: Makes tenant isolation clear, reflects business hierarchy
- **Flat**: Shared resources don't need tenant scoping, simpler API for code lookup

---

### 3. Pagination Strategy

**Decision**: Use page-based pagination with `page` and `limit` parameters.

**Rationale**:
- **Simplicity**: Easy to implement and understand
- **Performance**: Works well with SQL `OFFSET/LIMIT`
- **User Experience**: Clear navigation (page 1, 2, 3...)

**Response Format**:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

**Alternative Considered**: Cursor-based pagination
- **Rejected**: More complex, less intuitive for users, harder to implement with multiple sort criteria

---

### 4. Bulk Operations

**Decision**: Provide bulk code assignment endpoint for efficiency.

**Rationale**:
- **Performance**: Reduces API calls (1 request vs. N requests)
- **Atomicity**: Can ensure all codes assigned together or none
- **User Experience**: Faster for users assigning multiple codes

**Implementation**:
- Single transaction for all assignments
- Returns all created assignments in one response
- Updates encounter billing status automatically

---

### 5. Response Format Standardization

**Decision**: Consistent response format with embedded related resources where appropriate.

**Rationale**:
- **Reduced API Calls**: Include related data (e.g., patient info in encounter response)
- **Predictability**: Consistent structure across endpoints
- **Performance**: Fewer round trips for common use cases

**Example**: Encounter response includes patient and provider objects, not just IDs.

---

## Versioning Strategy

### API Versioning

**Decision**: URL path versioning (`/v1/`, `/v2/`).

**Rationale**:
- **Explicit**: Version in URL is clear and unambiguous
- **Backward Compatibility**: Can maintain multiple versions simultaneously
- **Industry Standard**: Common REST API versioning approach

**Policy**:
- Maintain at least one previous version when releasing new version
- Deprecation notice 6 months before removal
- Breaking changes only in major versions

---

### Code Set Versioning

**Decision**: Version column in code tables, not separate versioned tables.

**Rationale**:
- **Simplicity**: Single table per code type
- **Query Efficiency**: Can filter by version in WHERE clause
- **Storage Efficiency**: Avoid duplicate code entries

**Management**:
- New code sets imported with new version number
- Old assignments retain references to original code versions
- Default to latest version in searches, but allow version specification

---

## Security & Privacy

### 1. Data Isolation

**Implementation**:
- Application-level filtering by `organization_id` in all queries
- Optional database-level RLS policies as defense-in-depth
- Authentication middleware validates user belongs to organization

**Compliance**:
- HIPAA compliance through data segregation
- Audit logs track all data access

---

### 2. Sensitive Data Handling

**Decision**: Store SSN and other PII, but encrypt at application level.

**Rationale**:
- **Encryption at Rest**: Database encryption (TDE) protects data at rest
- **Encryption in Transit**: TLS for all API communications
- **Application Encryption**: Additional encryption for highly sensitive fields (SSN)
- **Access Controls**: Role-based access control (RBAC) limits who can view PII

**Future Enhancement**: Consider field-level encryption or tokenization for SSN.

---

### 3. Audit Logging

**Decision**: Comprehensive audit trail for code assignments.

**Rationale**:
- **Compliance**: Healthcare billing requires auditability
- **Security**: Track unauthorized changes
- **Quality**: Monitor coding accuracy and patterns

**Implementation**:
- Separate history table stores all changes
- Includes user, timestamp, action, and before/after values
- Immutable (no updates or deletes)

---

## Scalability Considerations

### 1. Database Sharding

**Future Strategy**: Shard by `organization_id` when single database becomes bottleneck.

**Implementation Path**:
- Current design supports sharding (organization_id in all queries)
- Can migrate to separate databases per organization group
- API gateway routes requests to appropriate shard

---

### 2. Caching Strategy

**Recommended Caching**:
- **Code Lookups**: Cache ICD/CPT code searches (rarely change)
- **Patient Lookups**: Cache frequently accessed patient records
- **Organization Metadata**: Cache organization info

**Cache Invalidation**:
- Code caches invalidated on code set updates
- Patient caches invalidated on updates (TTL-based)
- Use Redis for distributed caching

---

### 3. Read Replicas

**Strategy**: Use read replicas for reporting and analytics queries.

**Rationale**:
- **Performance**: Offload read-heavy workloads
- **Analytics**: Complex queries don't impact transactional performance
- **Scalability**: Add more replicas as load increases

---

## Future Extensibility

### 1. Support for Additional Code Types

**Design**: Easy to add HCPCS, LOINC, or other code types.

**Implementation**:
- Follow same pattern as ICD/CPT (separate table, assignment table)
- Add endpoints following same REST patterns
- Minimal changes to core schema

---

### 2. AI/ML Integration

**Design**: Architecture supports AI predictions.

**Features**:
- `confidence_score` in assignment tables (from NLP models)
- `is_confirmed` flag for human review workflow
- Assignment history tracks AI vs. human assignments
- Can add model version tracking

---

### 3. Workflow Management

**Future Enhancement**: Add coding workflow states.

**Potential Schema Addition**:
```sql
ALTER TABLE encounters 
ADD COLUMN coding_workflow_state VARCHAR(50) 
DEFAULT 'pending_review';
```

**States**: `pending_review`, `under_review`, `approved`, `needs_correction`

---

### 4. Multi-Language Support

**Future Enhancement**: Internationalize code descriptions.

**Implementation**:
- Add `language_code` to code tables
- Store translations in separate `code_translations` table
- API accepts `Accept-Language` header

---

## Summary

This design prioritizes:
1. **Multi-Tenancy**: Organization-based data isolation
2. **Compliance**: Audit trails and data retention
3. **Flexibility**: Versioning and extensibility
4. **Performance**: Comprehensive indexing and caching support
5. **Security**: Data isolation and encryption
6. **Scalability**: Sharding-ready architecture

The architecture balances current needs with future growth, ensuring the system can evolve as requirements change while maintaining data integrity and compliance with healthcare regulations.

