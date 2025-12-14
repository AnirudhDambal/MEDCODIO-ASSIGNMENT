# REST API Design

## Base URL
```
https://api.medcoding.com/v1
```

## Authentication
All endpoints require authentication via Bearer token:
```
Authorization: Bearer <access_token>
```

## Multi-Tenancy
The `organization_id` is extracted from the authenticated user's context. All operations are scoped to the user's organization.

---

## 1. Organizations APIs

### 1.1 Create Organization
**POST** `/organizations`

**Request Body:**
```json
{
  "organization_name": "General Hospital",
  "organization_code": "GH001",
  "address_line1": "123 Medical Center Dr",
  "city": "Boston",
  "state": "MA",
  "zip_code": "02115",
  "phone": "617-555-0100",
  "email": "admin@generalhospital.com",
  "tax_id": "12-3456789"
}
```

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "organization_name": "General Hospital",
  "organization_code": "GH001",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### 1.2 Get Organization
**GET** `/organizations/{organization_id}`

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "organization_name": "General Hospital",
  "organization_code": "GH001",
  "address_line1": "123 Medical Center Dr",
  "city": "Boston",
  "state": "MA",
  "zip_code": "02115",
  "phone": "617-555-0100",
  "email": "admin@generalhospital.com",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### 1.3 Update Organization
**PUT** `/organizations/{organization_id}`

**Request Body:** (same as create, all fields optional)

**Response:** `200 OK` (same as get)

---

### 1.4 List Organizations
**GET** `/organizations?status=active&page=1&limit=20`

**Query Parameters:**
- `status` (optional): Filter by status (`active`, `inactive`, `suspended`)
- `page` (optional, default: 1): Page number
- `limit` (optional, default: 20, max: 100): Items per page

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "...",
      "organization_name": "...",
      "organization_code": "...",
      "status": "active"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "total_pages": 3
  }
}
```

---

## 2. Providers APIs

### 2.1 Create Provider
**POST** `/organizations/{organization_id}/providers`

**Request Body:**
```json
{
  "provider_npi": "1234567890",
  "first_name": "John",
  "last_name": "Smith",
  "middle_name": "A",
  "title": "MD",
  "specialty": "Cardiology",
  "license_number": "MD12345",
  "email": "john.smith@hospital.com",
  "phone": "617-555-0101"
}
```

**Response:** `201 Created`
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "organization_id": "550e8400-e29b-41d4-a716-446655440000",
  "provider_npi": "1234567890",
  "first_name": "John",
  "last_name": "Smith",
  "title": "MD",
  "specialty": "Cardiology",
  "status": "active",
  "created_at": "2024-01-15T10:35:00Z"
}
```

---

### 2.2 Get Provider
**GET** `/organizations/{organization_id}/providers/{provider_id}`

**Response:** `200 OK` (full provider object)

---

### 2.3 Update Provider
**PUT** `/organizations/{organization_id}/providers/{provider_id}`

**Request Body:** (same as create, all fields optional)

**Response:** `200 OK`

---

### 2.4 List Providers
**GET** `/organizations/{organization_id}/providers?status=active&specialty=Cardiology&page=1&limit=20`

**Query Parameters:**
- `status` (optional): Filter by status
- `specialty` (optional): Filter by specialty
- `search` (optional): Search by name or NPI
- `page`, `limit`: Pagination

**Response:** `200 OK` (paginated list)

---

### 2.5 Delete Provider (Soft Delete)
**DELETE** `/organizations/{organization_id}/providers/{provider_id}`

**Response:** `204 No Content`

---

## 3. Patients APIs

### 3.1 Create Patient
**POST** `/organizations/{organization_id}/patients`

**Request Body:**
```json
{
  "patient_mrn": "MRN-001234",
  "first_name": "Jane",
  "last_name": "Doe",
  "middle_name": "M",
  "date_of_birth": "1985-05-15",
  "gender": "F",
  "ssn": "123-45-6789",
  "address_line1": "456 Main St",
  "city": "Boston",
  "state": "MA",
  "zip_code": "02116",
  "phone": "617-555-0200",
  "email": "jane.doe@email.com",
  "insurance_provider": "Blue Cross",
  "insurance_member_id": "BC123456"
}
```

**Response:** `201 Created`
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "organization_id": "550e8400-e29b-41d4-a716-446655440000",
  "patient_mrn": "MRN-001234",
  "first_name": "Jane",
  "last_name": "Doe",
  "date_of_birth": "1985-05-15",
  "gender": "F",
  "status": "active",
  "created_at": "2024-01-15T10:40:00Z"
}
```

---

### 3.2 Get Patient
**GET** `/organizations/{organization_id}/patients/{patient_id}`

**Response:** `200 OK` (full patient object)

---

### 3.3 Get Patient by MRN
**GET** `/organizations/{organization_id}/patients/mrn/{patient_mrn}`

**Response:** `200 OK` (full patient object)

---

### 3.4 Update Patient
**PUT** `/organizations/{organization_id}/patients/{patient_id}`

**Request Body:** (same as create, all fields optional)

**Response:** `200 OK`

---

### 3.5 List Patients
**GET** `/organizations/{organization_id}/patients?status=active&search=Jane&page=1&limit=20`

**Query Parameters:**
- `status` (optional): Filter by status
- `search` (optional): Search by name or MRN
- `page`, `limit`: Pagination

**Response:** `200 OK` (paginated list)

---

### 3.6 Delete Patient (Soft Delete)
**DELETE** `/organizations/{organization_id}/patients/{patient_id}`

**Response:** `204 No Content`

---

## 4. Encounters APIs

### 4.1 Create Encounter
**POST** `/organizations/{organization_id}/encounters`

**Request Body:**
```json
{
  "patient_id": "770e8400-e29b-41d4-a716-446655440002",
  "provider_id": "660e8400-e29b-41d4-a716-446655440001",
  "encounter_type": "office_visit",
  "encounter_date": "2024-01-20",
  "encounter_time": "14:30:00",
  "chief_complaint": "Chest pain and shortness of breath",
  "visit_status": "scheduled",
  "notes": "Patient reports chest pain lasting 2 hours"
}
```

**Response:** `201 Created`
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "organization_id": "550e8400-e29b-41d4-a716-446655440000",
  "patient_id": "770e8400-e29b-41d4-a716-446655440002",
  "provider_id": "660e8400-e29b-41d4-a716-446655440001",
  "encounter_type": "office_visit",
  "encounter_date": "2024-01-20",
  "encounter_time": "14:30:00",
  "chief_complaint": "Chest pain and shortness of breath",
  "visit_status": "scheduled",
  "billing_status": "pending",
  "created_at": "2024-01-15T11:00:00Z"
}
```

---

### 4.2 Get Encounter
**GET** `/organizations/{organization_id}/encounters/{encounter_id}`

**Response:** `200 OK`
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "organization_id": "550e8400-e29b-41d4-a716-446655440000",
  "patient": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "patient_mrn": "MRN-001234",
    "first_name": "Jane",
    "last_name": "Doe"
  },
  "provider": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "provider_npi": "1234567890",
    "first_name": "John",
    "last_name": "Smith",
    "title": "MD"
  },
  "encounter_type": "office_visit",
  "encounter_date": "2024-01-20",
  "encounter_time": "14:30:00",
  "chief_complaint": "Chest pain and shortness of breath",
  "visit_status": "completed",
  "billing_status": "coded",
  "notes": "Patient reports chest pain lasting 2 hours",
  "icd_codes": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440004",
      "code": "I10",
      "description": "Essential (primary) hypertension",
      "assignment_type": "primary",
      "is_confirmed": true
    }
  ],
  "cpt_codes": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "code": "99213",
      "description": "Office or other outpatient visit",
      "quantity": 1,
      "is_confirmed": true
    }
  ],
  "created_at": "2024-01-15T11:00:00Z",
  "updated_at": "2024-01-20T15:30:00Z"
}
```

---

### 4.3 Update Encounter
**PUT** `/organizations/{organization_id}/encounters/{encounter_id}`

**Request Body:** (same as create, all fields optional)

**Response:** `200 OK`

---

### 4.4 List Encounters
**GET** `/organizations/{organization_id}/encounters?patient_id={id}&provider_id={id}&date_from=2024-01-01&date_to=2024-01-31&billing_status=pending&page=1&limit=20`

**Query Parameters:**
- `patient_id` (optional): Filter by patient
- `provider_id` (optional): Filter by provider
- `date_from`, `date_to` (optional): Date range filter
- `encounter_type` (optional): Filter by type
- `visit_status` (optional): Filter by visit status
- `billing_status` (optional): Filter by billing status
- `page`, `limit`: Pagination

**Response:** `200 OK` (paginated list)

---

### 4.5 Delete Encounter (Soft Delete)
**DELETE** `/organizations/{organization_id}/encounters/{encounter_id}`

**Response:** `204 No Content`

---

## 5. Medical Codes APIs

### 5.1 Search ICD Codes
**GET** `/medical-codes/icd?search=hypertension&version=2024&page=1&limit=20`

**Query Parameters:**
- `search` (optional): Search by code or description
- `version` (optional, default: latest): ICD code version
- `category` (optional): Filter by category
- `is_valid` (optional, default: true): Filter by validity
- `page`, `limit`: Pagination

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "bb0e8400-e29b-41d4-a716-446655440006",
      "code": "I10",
      "code_version": "2024",
      "short_description": "Essential (primary) hypertension",
      "long_description": "Hypertension, essential...",
      "category": "Diseases of the circulatory system",
      "is_valid": true
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 5,
    "total_pages": 1
  }
}
```

---

### 5.2 Get ICD Code
**GET** `/medical-codes/icd/{icd_code_id}`

**Response:** `200 OK` (full ICD code object)

---

### 5.3 Search CPT Codes
**GET** `/medical-codes/cpt?search=office visit&version=2024&page=1&limit=20`

**Query Parameters:** (same as ICD codes)

**Response:** `200 OK` (similar format to ICD codes)

---

### 5.4 Get CPT Code
**GET** `/medical-codes/cpt/{cpt_code_id}`

**Response:** `200 OK` (full CPT code object)

---

## 6. Code Assignment APIs

### 6.1 Assign ICD Code to Encounter
**POST** `/organizations/{organization_id}/encounters/{encounter_id}/icd-codes`

**Request Body:**
```json
{
  "icd_code_id": "bb0e8400-e29b-41d4-a716-446655440006",
  "assignment_type": "primary",
  "notes": "Confirmed diagnosis",
  "confidence_score": 95.5,
  "is_confirmed": true
}
```

**Response:** `201 Created`
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440004",
  "encounter_id": "880e8400-e29b-41d4-a716-446655440003",
  "icd_code": {
    "code": "I10",
    "description": "Essential (primary) hypertension"
  },
  "assignment_type": "primary",
  "is_confirmed": true,
  "confidence_score": 95.5,
  "assigned_at": "2024-01-20T15:45:00Z"
}
```

---

### 6.2 Update ICD Code Assignment
**PUT** `/organizations/{organization_id}/encounters/{encounter_id}/icd-codes/{assignment_id}`

**Request Body:** (same as create, all fields optional)

**Response:** `200 OK`

---

### 6.3 Remove ICD Code Assignment
**DELETE** `/organizations/{organization_id}/encounters/{encounter_id}/icd-codes/{assignment_id}`

**Response:** `204 No Content`

---

### 6.4 Assign CPT Code to Encounter
**POST** `/organizations/{organization_id}/encounters/{encounter_id}/cpt-codes`

**Request Body:**
```json
{
  "cpt_code_id": "cc0e8400-e29b-41d4-a716-446655440007",
  "quantity": 1,
  "modifier_1": "25",
  "modifier_2": null,
  "units": 1.0,
  "notes": "Office visit with procedure",
  "confidence_score": 92.0,
  "is_confirmed": true
}
```

**Response:** `201 Created` (similar format to ICD assignment)

---

### 6.5 Update CPT Code Assignment
**PUT** `/organizations/{organization_id}/encounters/{encounter_id}/cpt-codes/{assignment_id}`

**Request Body:** (same as create, all fields optional)

**Response:** `200 OK`

---

### 6.6 Remove CPT Code Assignment
**DELETE** `/organizations/{organization_id}/encounters/{encounter_id}/cpt-codes/{assignment_id}`

**Response:** `204 No Content`

---

### 6.7 Bulk Assign Codes to Encounter
**POST** `/organizations/{organization_id}/encounters/{encounter_id}/codes/bulk`

**Request Body:**
```json
{
  "icd_codes": [
    {
      "icd_code_id": "bb0e8400-e29b-41d4-a716-446655440006",
      "assignment_type": "primary",
      "is_confirmed": true
    }
  ],
  "cpt_codes": [
    {
      "cpt_code_id": "cc0e8400-e29b-41d4-a716-446655440007",
      "quantity": 1,
      "is_confirmed": true
    }
  ]
}
```

**Response:** `201 Created`
```json
{
  "icd_assignments": [...],
  "cpt_assignments": [...],
  "encounter_billing_status": "coded"
}
```

---

## 7. Modifier Rule APIs

### 7.1 Get Valid Modifiers for CPT Code
**GET** `/medical-codes/cpt/{cpt_code_id}/valid-modifiers?version=2024`

**Query Parameters:**
- `version` (optional, default: latest): CPT code version
- `effective_date` (optional): Check validity on a specific date

**Response:** `200 OK`
```json
{
  "cpt_code": {
    "id": "cc0e8400-e29b-41d4-a716-446655440007",
    "code": "45378",
    "description": "Colonoscopy, flexible; with directed submucosal injection(s)"
  },
  "valid_modifiers": [
    {
      "code": "25",
      "description": "Significant, separately identifiable evaluation and management service",
      "category": "Evaluation",
      "is_allowed": true,
      "notes": "Can be used when E&M service is performed on the same day"
    },
    {
      "code": "59",
      "description": "Distinct procedural service",
      "category": "Surgical",
      "is_allowed": true,
      "notes": "Use when procedure is distinct from other services"
    },
    {
      "code": "LT",
      "description": "Left side",
      "category": "Anatomic",
      "is_allowed": true
    },
    {
      "code": "RT",
      "description": "Right side",
      "category": "Anatomic",
      "is_allowed": true
    }
  ],
  "disallowed_modifiers": [
    {
      "code": "50",
      "description": "Bilateral procedure",
      "is_allowed": false,
      "notes": "Not applicable to colonoscopy procedures"
    }
  ]
}
```

---

### 7.2 Get All Modifiers (Reference)
**GET** `/medical-codes/modifiers?category=Surgical&active_only=true`

**Query Parameters:**
- `category` (optional): Filter by modifier category
- `active_only` (optional, default: true): Return only active modifiers

**Response:** `200 OK`
```json
{
  "data": [
    {
      "code": "25",
      "description": "Significant, separately identifiable evaluation and management service",
      "category": "Evaluation",
      "is_active": true
    },
    {
      "code": "59",
      "description": "Distinct procedural service",
      "category": "Surgical",
      "is_active": true
    }
  ],
  "total": 50
}
```

---

### 7.3 Validate Modifier for CPT Code
**POST** `/medical-codes/cpt/{cpt_code_id}/validate-modifier`

**Request Body:**
```json
{
  "modifier_code": "25",
  "cpt_code_version": "2024"
}
```

**Response:** `200 OK`
```json
{
  "is_valid": true,
  "modifier": {
    "code": "25",
    "description": "Significant, separately identifiable evaluation and management service"
  },
  "rule": {
    "is_allowed": true,
    "notes": "Can be used when E&M service is performed on the same day",
    "effective_date": "2024-01-01"
  }
}
```

If invalid:
```json
{
  "is_valid": false,
  "modifier": {
    "code": "50",
    "description": "Bilateral procedure"
  },
  "reason": "This modifier is not allowed for the specified CPT code",
  "rule": {
    "is_allowed": false,
    "notes": "Not applicable to colonoscopy procedures"
  }
}
```

---

## 8. Code Assignment History APIs

### 8.1 Get Assignment History
**GET** `/organizations/{organization_id}/encounters/{encounter_id}/code-history?assignment_type=icd&page=1&limit=20`

**Query Parameters:**
- `assignment_type` (optional): Filter by `icd` or `cpt`
- `date_from`, `date_to` (optional): Date range
- `page`, `limit`: Pagination

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "dd0e8400-e29b-41d4-a716-446655440008",
      "assignment_type": "icd",
      "assignment_id": "990e8400-e29b-41d4-a716-446655440004",
      "action": "created",
      "old_value": null,
      "new_value": {
        "code": "I10",
        "assignment_type": "primary"
      },
      "changed_by": "user-id",
      "changed_at": "2024-01-20T15:45:00Z",
      "reason": "Initial diagnosis assignment"
    }
  ],
  "pagination": {...}
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "provider_npi",
        "message": "NPI must be exactly 10 digits"
      }
    ],
    "timestamp": "2024-01-15T12:00:00Z",
    "request_id": "req-123456"
  }
}
```

### Common HTTP Status Codes:
- `200 OK`: Successful GET/PUT
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., duplicate NPI)
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

## API Versioning

Version is included in the URL path: `/v1/...`

Future versions will use `/v2/...`, etc., with backward compatibility maintained for at least one previous version.

---

## Rate Limiting

- **Standard**: 1000 requests per hour per organization
- **Premium**: 5000 requests per hour per organization

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

