# Koala ACT - API Documentation for Frontend

## Base URL
```
Development: http://localhost:8001/api/v1
Production: https://your-domain.com/api/v1
```

## Swagger UI
```
http://localhost:8001/docs
```

---

## Authentication

### 1. Dev Login (только для разработки)
```http
POST /auth/dev-login
Content-Type: application/json

{
  "email": "test@test.com"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "user_id": 1,
  "email": "test@test.com"
}
```

### 2. Google OAuth (production)
```http
GET /auth/google?platform=mobile&redirect_uri=koalaact://callback
```
- `platform`: "web" | "mobile"
- `redirect_uri`: deep link для mobile

### 3. Logout
```http
POST /auth/logout
```

### Использование токена
Все защищенные endpoints требуют header:
```
Authorization: Bearer <access_token>
```

---

## User Profile

### Get Profile
```http
GET /users/profile
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "email": "test@test.com",
  "full_name": "Test User",
  "current_score": 25,
  "target_score": 36,
  "exam_date": "2024-06-01T00:00:00",
  "has_onboard": true,
  "is_admin": false
}
```

### Update Profile
```http
PATCH /users/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "New Name",
  "target_score": 32,
  "exam_date": "2024-07-01T00:00:00",
  "has_onboard": true
}
```

**Все поля опциональны.** Можно обновить только нужные:
- `full_name` - имя пользователя
- `current_score` - текущий балл
- `target_score` - целевой балл
- `exam_date` - дата экзамена
- `has_onboard` - завершён ли онбординг

### Get User Buildings (Castle + Villages)
```http
GET /users/buildings
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "svg": "https://storage.example.com/castle.svg",
  "treasure_amount": 150,
  "last_collect_date": "2024-01-15T10:30:00",
  "taps_used_today": 3,
  "last_tap_reset_date": "2024-01-15",
  "speed_production_treasure": 10,
  "villages": [
    {
      "id": 2,
      "svg": "https://storage.example.com/math-village.svg",
      "subject": "math",
      "treasure_amount": 50,
      "last_collect_date": "2024-01-15T09:00:00",
      "last_update_at": "2024-01-15T12:00:00",
      "speed_production_treasure": 5
    },
    {
      "id": 3,
      "svg": "https://storage.example.com/english-village.svg",
      "subject": "english",
      "treasure_amount": 30,
      "last_collect_date": null,
      "last_update_at": null,
      "speed_production_treasure": 5
    }
  ]
}
```

---

## Onboarding

### 1. Get Passages for Subject (что показывать на онбординге)
```http
GET /onboards/passages?subject=math
Authorization: Bearer <token>
```

**Subjects:** `math`, `english`, `reading`, `science`

**Response:**
```json
[
  {
    "id": 1,
    "title": "Algebra",
    "order_index": 1
  },
  {
    "id": 2,
    "title": "Geometry",
    "order_index": 2
  }
]
```

### 2. Complete Onboarding (User Acquaintance)
```http
POST /onboards/user/acquaintance
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_score": 25,
  "target_score": 32,
  "exam_date": "2024-06-01T00:00:00",
  "subjects": [
    {
      "subject": "math",
      "passages": [
        {"passage_id": 1, "user_level": "weak"},
        {"passage_id": 2, "user_level": "know_not_good"},
        {"passage_id": 3, "user_level": "strong"}
      ]
    },
    {
      "subject": "english",
      "passages": [
        {"passage_id": 4, "user_level": "no_idea"},
        {"passage_id": 5, "user_level": "weak"}
      ]
    }
  ]
}
```

**user_level values:**
- `no_idea` - Не знаю вообще
- `know_not_good` - Знаю, но плохо
- `weak` - Слабо
- `strong` - Хорошо знаю

### 3. Subject Onboard (для одного предмета)
```http
POST /onboards/subject
Authorization: Bearer <token>
Content-Type: application/json

{
  "subject": "math",
  "passages": [
    {"passage_id": 1, "user_level": "weak"},
    {"passage_id": 2, "user_level": "strong"}
  ]
}
```

---

## Roadmap & Learning

### Get Roadmap by Subject
```http
GET /roadmaps/{subject}
Authorization: Bearer <token>
```

**Subjects:** `math`, `english`, `reading`, `science`

**Response:**
```json
[
  {
    "id": 1,
    "title": "Algebra Basics",
    "order_index": 1,
    "status": "available",
    "nodes": [
      {
        "id": 10,
        "title": "Variables and Expressions",
        "content": "Learn about...",
        "is_completed": true,
        "is_locked": false,
        "is_current": false
      },
      {
        "id": 11,
        "title": "Solving Equations",
        "content": "Practice solving...",
        "is_completed": false,
        "is_locked": false,
        "is_current": true
      },
      {
        "id": 12,
        "title": "Word Problems",
        "content": null,
        "is_completed": false,
        "is_locked": true,
        "is_current": false
      }
    ],
    "boss": {
      "id": 15,
      "title": "Algebra Challenge",
      "content": "Final test...",
      "config": {},
      "is_completed": false,
      "is_locked": true,
      "pass_score": 70,
      "reward_coins": 50
    }
  },
  {
    "id": 2,
    "title": "Linear Equations",
    "order_index": 2,
    "status": "locked",
    "nodes": [...],
    "boss": {...}
  }
]
```

**Status values:**
- `available` - Можно проходить
- `locked` - Заблокирован (нужно пройти предыдущий)
- `completed` - Пройден

### Get Node Details (with questions)
```http
GET /roadmaps/nodes/{node_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 11,
  "title": "Solving Equations",
  "content": "Learn how to solve linear equations...",
  "is_boss": false,
  "pass_score": null,
  "reward_coins": null,
  "reward_xp": null,
  "questions": [
    {
      "id": 101,
      "node_id": 11,
      "type": "fill_gap",
      "content": {
        "question": "If $2x + 10 = 20$, then $x = ?$",
        "correct_answer": "5",
        "explanation": "Subtract 10, divide by 2"
      },
      "order_index": 1
    },
    {
      "id": 102,
      "node_id": 11,
      "type": "multiple_choice",
      "content": {
        "question": "Which is correct?",
        "options": [
          {"id": "a", "text": "2x = 10", "is_correct": true},
          {"id": "b", "text": "2x = 20", "is_correct": false}
        ],
        "explanation": "..."
      },
      "order_index": 2
    },
    {
      "id": 103,
      "node_id": 11,
      "type": "matching",
      "content": {
        "left_items": [
          {"id": "l1", "text": "2(x+4)"},
          {"id": "l2", "text": "(3x)²"}
        ],
        "right_items": [
          {"id": "r1", "text": "9x²"},
          {"id": "r2", "text": "2x+8"}
        ],
        "correct_pairs": [
          {"left_id": "l1", "right_id": "r2"},
          {"left_id": "l2", "right_id": "r1"}
        ]
      },
      "order_index": 3
    }
  ]
}
```

---

## Submit Answers

### Submit Quiz Answers
```http
POST /submits
Authorization: Bearer <token>
Content-Type: application/json

{
  "node_id": 11,
  "questions": [
    {
      "question_id": 101,
      "question_type": "fill_gap",
      "content": {"answer": "5"}
    },
    {
      "question_id": 102,
      "question_type": "multiple_choice",
      "content": {"options": [{"id": "a"}]}
    },
    {
      "question_id": 103,
      "question_type": "matching",
      "content": {
        "pairs": [
          {"left_id": "l1", "right_id": "r2"},
          {"left_id": "l2", "right_id": "r1"}
        ]
      }
    }
  ]
}
```

**Response:**
```json
{
  "earned_xp": 10,
  "earned_coins": 5,
  "accuracy": 0.8,
  "correct_answers": 4,
  "total_questions": 5,
  "is_completed": true,
  "next_node_unlocked": true,
  "next_node_id": 12
}
```

### All Question Types & Submit Formats

#### 1. fill_gap
```json
// Question
{"type": "fill_gap", "content": {"question": "2+2=?", "correct_answer": "4"}}

// Submit
{"question_type": "fill_gap", "content": {"answer": "4"}}
```

#### 2. multiple_choice
```json
// Question
{"type": "multiple_choice", "content": {"options": [{"id": "a", "is_correct": true}, {"id": "b", "is_correct": false}]}}

// Submit (can select multiple)
{"question_type": "multiple_choice", "content": {"options": [{"id": "a"}, {"id": "c"}]}}
```

#### 3. matching
```json
// Question
{
  "type": "matching",
  "content": {
    "left_items": [{"id": "l1", "text": "A"}, {"id": "l2", "text": "B"}],
    "right_items": [{"id": "r1", "text": "1"}, {"id": "r2", "text": "2"}],
    "correct_pairs": [{"left_id": "l1", "right_id": "r2"}]
  }
}

// Submit
{"question_type": "matching", "content": {"pairs": [{"left_id": "l1", "right_id": "r2"}]}}
```

#### 4. ordering
```json
// Question
{"type": "ordering", "content": {"items": [{"id": "1", "content": "First"}, {"id": "2", "content": "Second"}], "correct_order": ["1", "2"]}}

// Submit
{"question_type": "ordering", "content": {"ordered_items": ["1", "2"]}}
```

#### 5. find_error
```json
// Question
{"type": "find_error", "content": {"sentence": "The dog are running", "error_index": 2}}

// Submit
{"question_type": "find_error", "content": {"error_index": 2}}
```

#### 6. strike_out
```json
// Question
{"type": "strike_out", "content": {"sentence": "The wet rain fell", "correct_ids_to_remove": [1]}}

// Submit
{"question_type": "strike_out", "content": {"removed_ids": [1]}}
```

#### 7. highlight
```json
// Question
{"type": "highlight", "content": {"passage": "The cat sat on mat", "correct_phrase": "cat"}}

// Submit
{"question_type": "highlight", "content": {"selected_phrase": "cat"}}
```

#### 8. swipe_decision
```json
// Question
{"type": "swipe_decision", "content": {"correct_swipe": "left", "labels": {"left": "Fact", "right": "Opinion"}}}

// Submit
{"question_type": "swipe_decision", "content": {"swipe": "left"}}
```

#### 9. graph_point
```json
// Question
{"type": "graph_point", "content": {"target_x": 2, "target_y": 3, "radius": 15}}

// Submit
{"question_type": "graph_point", "content": {"x": 2.1, "y": 2.9}}
```

#### 10. trend_arrow
```json
// Question
{"type": "trend_arrow", "content": {"correct_trend": "increase"}}

// Submit (values: "increase", "decrease", "no_change")
{"question_type": "trend_arrow", "content": {"trend": "increase"}}
```

#### 11. slider_value
```json
// Question
{"type": "slider_value", "content": {"min_value": 0, "max_value": 100, "correct_value": 50, "tolerance": 5}}

// Submit
{"question_type": "slider_value", "content": {"value": 48}}
```

---

## Collectors (Treasure System)

### Get Castle Status
```http
GET /collectors/castle/status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "castle_id": 1,
  "castle_title": "Starter Castle",
  "treasure": {
    "current_amount": 150,
    "capacity": 500,
    "production_rate": 10,
    "last_collect_date": "2024-01-15T10:30:00",
    "time_to_full_minutes": 35,
    "fund_type": "crystal"
  },
  "taps_remaining": 7,
  "max_taps_per_day": 10,
  "coins_per_tap": 5
}
```

### Collect Castle Treasure (Crystals)
```http
POST /collectors/castle/collect
Authorization: Bearer <token>
```

**Response:**
```json
{
  "collected_amount": 150,
  "fund_type": "crystal",
  "new_wallet_balance": 500
}
```

### Tap (Earn Coins)
```http
POST /collectors/castle/tap
Authorization: Bearer <token>
Content-Type: application/json

{"tapped": 1}
```

**Response:**
```json
{
  "coins_collected": 5,
  "taps_remaining": 6,
  "new_wallet_balance": 125
}
```

### Get Village Status
```http
GET /collectors/village/{village_id}/status
Authorization: Bearer <token>
```

### Collect Village Treasure (Coins)
```http
POST /collectors/village/{village_id}/collect
Authorization: Bearer <token>
```

### Get All Villages Status
```http
GET /collectors/villages/status
Authorization: Bearer <token>
```

---

## Progression (Upgrades)

### Castle Upgrade Info
```http
GET /progression/castle/upgrade-info
Authorization: Bearer <token>
```

**Response:**
```json
{
  "can_upgrade": true,
  "current_level": 1,
  "next_level": 2,
  "upgrade_cost": 500,
  "cost_fund_type": "crystal",
  "current_balance": 600,
  "reason": null
}
```

### Upgrade Castle
```http
POST /progression/castle/upgrade
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "new_level": 2,
  "cost_paid": 500,
  "new_balance": 100
}
```

### Village Upgrade Info
```http
GET /progression/village/{subject}/upgrade-info
Authorization: Bearer <token>
```
**Subjects:** `math`, `english`, `reading`, `science`

### Upgrade Village
```http
POST /progression/village/{subject}/upgrade
Authorization: Bearer <token>
```

---

## Dev Endpoints (DEBUG=True only)

### Seed Test Data
```http
POST /dev/seed-data
Authorization: Bearer <token>
```
Creates Castle + Villages for test user.

### Check Progress
```http
GET /dev/my-progress
Authorization: Bearer <token>
```

**Response:**
```json
{
  "user_id": 1,
  "experience": {"level": 2, "current_xp": 150},
  "wallets": [
    {"fund_type": "coin", "fund": 250},
    {"fund_type": "crystal", "fund": 50}
  ],
  "completed_nodes": [
    {"node_id": 10, "accuracy": 1.0, "xp": 10, "correct_answer": 5},
    {"node_id": 11, "accuracy": 0.8, "xp": 10, "correct_answer": 4}
  ],
  "total_completed": 2
}
```

### Clear Questions (Regenerate)
```http
DELETE /dev/clear-questions
Authorization: Bearer <token>
```

### Check Dev Mode
```http
GET /dev/check
```

### Reset Onboard (для тестирования онбординга заново)
```http
POST /dev/reset-onboard
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Onboard reset successfully",
  "user_id": 1,
  "has_onboard": false
}
```

---

## Typical User Flow

```
1. Login
   POST /auth/dev-login → get access_token

2. Check if onboarding needed
   GET /users/profile → check has_onboard

3. If has_onboard=false → Onboarding:
   a) GET /onboards/passages?subject=math → get passages list
   b) GET /onboards/passages?subject=english → repeat for each subject
   c) POST /onboards/user/acquaintance → submit user levels

4. Create test data (dev only)
   POST /dev/seed-data → creates castle + villages

5. Get buildings map
   GET /users/buildings → shows castle + 4 villages

6. Choose subject and get roadmap
   GET /roadmaps/math → list of passages with nodes

7. Open node and get questions
   GET /roadmaps/nodes/11 → node details + questions

8. Submit answers
   POST /submits → returns earned_xp, next_node_id

9. Continue to next node or boss
   GET /roadmaps/nodes/12 → next node

10. Collect treasures
    POST /collectors/castle/collect → collect crystals
    POST /collectors/village/2/collect → collect coins

11. Upgrade buildings
    POST /progression/village/math/upgrade → upgrade village
```

---

## Error Responses

```json
// 400 Bad Request
{"detail": "Invalid input data"}

// 401 Unauthorized
{"detail": "Missing credentials"}

// 403 Forbidden
{"detail": "Admin access required"}

// 404 Not Found
{"detail": "Node not found"}

// 422 Validation Error
{
  "detail": [
    {
      "loc": ["body", "questions", 0, "content"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Constants

### Subjects
```
math, english, reading, science
```

### Fund Types
```
coin - from villages, used for village upgrades
crystal - from castle, used for castle upgrades
```

### Question Types
```
fill_gap, multiple_choice, matching, ordering,
find_error, strike_out, highlight, swipe_decision,
graph_point, trend_arrow, slider_value
```

### User Levels (for onboarding)
```
no_idea, know_not_good, weak, strong
```
