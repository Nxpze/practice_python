# For-practice-my-python-for-data-analysis-skills
  
## Data set
let see what we have here to practice  
here is 3 file to practice cus you might need some file to merge when you learn Pandas
- [ecommerce order](Https://github.com/Nxpze/For-practice-my-python-for-data-analysis-skills/blob/33d59afe0ac88c0fc1400d6175590ca6c47fc4be/Dataset/ecommerce_orders_practice.csv)
- [customers](Https://github.com/Nxpze/For-practice-my-python-for-data-analysis-skills/blob/33d59afe0ac88c0fc1400d6175590ca6c47fc4be/Dataset/customers.csv)
- [category catalog](Https://github.com/Nxpze/For-practice-my-python-for-data-analysis-skills/blob/33d59afe0ac88c0fc1400d6175590ca6c47fc4be/Dataset/category_catalog.csv)

---
### test mermaid
```mermaid
erDiagram
    PATIENT ||--o{ MEDICAL_RECORD : "has"
    PATIENT ||--o{ BILL : "receives"
    MEDICAL_RECORD ||--|| BILL : "generates"

    PATIENT {
        string P_id PK
        string fullname
        date dob
        string phone_number
        string allergies
        string underlying_disease
    }


    MEDICAL_RECORD {
        string record_id PK
        string P_id FK
        string D_id FK
        date record_date
        string diagnosis
        string status
        string prescribed_meds
    }

    BILL {
        string bill_id PK
        string record_id FK
        string P_id FK
        decimal treatment_fee
        decimal medication_fee
        decimal total_payment
    }
```
