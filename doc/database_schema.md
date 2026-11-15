# Schema bazei de date

Schema reflectă modelele Django din aplicația `trips`. `USER` este tabela
Django `auth_user`; câmpurile care se termină în `_id` sunt chei străine.

```mermaid
erDiagram
    USER {
        int id PK
        string username
        string email
        string first_name
        string last_name
    }
    TRIP {
        int id PK
        string name
        string slug UK
        text description
        int organizer_id FK
        date departure_date
        date return_date
        decimal budget_per_person
        string currency
        int final_destination_id FK
        int final_accommodation_id FK
        int final_transfer_id FK
        datetime voting_closed_at
        datetime created_at
        datetime updated_at
    }
    TRIP_PARTICIPANT {
        int id PK
        int trip_id FK
        int user_id FK
        datetime joined_at
    }
    TRIP_INVITATION {
        int id PK
        int trip_id FK
        int created_by_id FK
        string email
        string token_hash UK
        datetime expires_at
        datetime accepted_at
        int accepted_by_id FK
        datetime revoked_at
        datetime created_at
    }
    DESTINATION {
        int id PK
        int trip_id FK
        string country
        string city
        text description
        string address
        string status
        int created_by_id FK
        decimal latitude
        decimal longitude
        datetime created_at
        datetime updated_at
    }
    DESTINATION_VOTE {
        int id PK
        int destination_id FK
        int user_id FK
        boolean value
        datetime created_at
        datetime updated_at
    }
    ACTIVITY_PROPOSAL {
        int id PK
        int destination_id FK
        int proposed_by_id FK
        string name
        text description
        string status
        decimal estimated_cost
        int duration_minutes
        datetime start_at
        decimal latitude
        decimal longitude
        datetime created_at
        datetime updated_at
    }
    ACTIVITY_SCORE {
        int id PK
        int activity_id FK
        int user_id FK
        int score
        datetime created_at
        datetime updated_at
    }
    ACCOMMODATION_PROPOSAL {
        int id PK
        int trip_id FK
        int proposed_by_id FK
        string name
        text description
        string address
        decimal estimated_cost
        string status
        datetime created_at
        datetime updated_at
    }
    ACCOMMODATION_VOTE {
        int id PK
        int trip_id FK
        int accommodation_id FK
        int user_id FK
        datetime created_at
        datetime updated_at
    }
    TRANSFER_PROPOSAL {
        int id PK
        int trip_id FK
        int proposed_by_id FK
        string name
        text description
        string route
        decimal estimated_cost
        int duration_minutes
        string status
        datetime created_at
        datetime updated_at
    }
    TRANSFER_VOTE {
        int id PK
        int trip_id FK
        int transfer_id FK
        int user_id FK
        datetime created_at
        datetime updated_at
    }
    ITINERARY {
        int id PK
        int destination_id FK
        datetime approved_at
        int approved_by_id FK
        datetime created_at
        datetime updated_at
    }
    ITINERARY_CONSTRAINT {
        int id PK
        int trip_id FK
        int created_by_id FK
        string title
        text description
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    ITINERARY_ITEM {
        int id PK
        int itinerary_id FK
        int activity_id FK
        datetime start_at
        int duration_minutes
        int position
        text reason
        datetime created_at
        datetime updated_at
    }
    EXPENSE {
        int id PK
        int trip_id FK
        int paid_by_id FK
        string description
        decimal amount
        string currency
        datetime occurred_at
        datetime created_at
        datetime updated_at
    }
    EXPENSE_SHARE {
        int id PK
        int expense_id FK
        int user_id FK
        decimal amount_owed
        datetime created_at
    }
    READ_ONLY_SHARE_LINK {
        int id PK
        int trip_id FK
        int created_by_id FK
        string token_hash UK
        datetime expires_at
        datetime revoked_at
        datetime created_at
    }

    USER ||--o{ TRIP : organizes
    USER ||--o{ TRIP_PARTICIPANT : joins
    TRIP ||--o{ TRIP_PARTICIPANT : has
    TRIP ||--o{ TRIP_INVITATION : sends
    USER ||--o{ TRIP_INVITATION : creates
    USER o|--o{ TRIP_INVITATION : accepts

    TRIP ||--o{ DESTINATION : proposes
    USER ||--o{ DESTINATION : proposes
    DESTINATION ||--o{ DESTINATION_VOTE : receives
    USER ||--o{ DESTINATION_VOTE : casts
    DESTINATION ||--o{ ACTIVITY_PROPOSAL : contains
    USER ||--o{ ACTIVITY_PROPOSAL : proposes
    ACTIVITY_PROPOSAL ||--o{ ACTIVITY_SCORE : receives
    USER ||--o{ ACTIVITY_SCORE : gives

    TRIP ||--o{ ACCOMMODATION_PROPOSAL : contains
    USER ||--o{ ACCOMMODATION_PROPOSAL : proposes
    TRIP ||--o{ ACCOMMODATION_VOTE : scopes
    ACCOMMODATION_PROPOSAL ||--o{ ACCOMMODATION_VOTE : receives
    USER ||--o{ ACCOMMODATION_VOTE : casts
    TRIP ||--o{ TRANSFER_PROPOSAL : contains
    USER ||--o{ TRANSFER_PROPOSAL : proposes
    TRIP ||--o{ TRANSFER_VOTE : scopes
    TRANSFER_PROPOSAL ||--o{ TRANSFER_VOTE : receives
    USER ||--o{ TRANSFER_VOTE : casts

    DESTINATION ||--o| ITINERARY : has
    USER o|--o{ ITINERARY : approves
    ITINERARY ||--o{ ITINERARY_ITEM : contains
    ACTIVITY_PROPOSAL ||--o{ ITINERARY_ITEM : scheduled
    TRIP ||--o{ ITINERARY_CONSTRAINT : defines
    USER ||--o{ ITINERARY_CONSTRAINT : creates

    TRIP ||--o{ EXPENSE : records
    USER ||--o{ EXPENSE : pays
    EXPENSE ||--o{ EXPENSE_SHARE : splits
    USER ||--o{ EXPENSE_SHARE : owes
    TRIP ||--o{ READ_ONLY_SHARE_LINK : exposes
    USER ||--o{ READ_ONLY_SHARE_LINK : creates

    TRIP o|--o| DESTINATION : final_destination
    TRIP o|--o| ACCOMMODATION_PROPOSAL : final_accommodation
    TRIP o|--o| TRANSFER_PROPOSAL : final_transfer
```

`Trip.total_budget` nu este o coloană persistentă; este calculat ca
`budget_per_person * numărul participanților`.

Constrângerile de unicitate importante sunt: un participant per pereche
`trip/user`, un vot per pereche propunere/utilizator, un scor per pereche
activitate/utilizator, un share per pereche cheltuială/utilizator și un singur
itinerar per destinație.
