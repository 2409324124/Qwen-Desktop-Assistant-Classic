Of course. Based on the specific DDL you provided, here is a complete, production-ready solution using Spring Boot, Hibernate, and a REST API.

This solution covers the entity, repository, service logic, and controller, designed to be robust and handle concurrency safely.

### Prerequisites: Database Setup

Before running the code, you need to make two small modifications in Oracle.

1.  **Create a Sequence for the Numeric ID:** The best practice in Oracle for generating unique, sequential numbers is to use a sequence. This is highly efficient and safe for concurrent usage. Let's call it `LC_IDENTIFIER_VAL_SEQ`.
    ```sql
    CREATE SEQUENCE LICENSEADMIN.LC_IDENTIFIER_VAL_SEQ
        START WITH 1
        INCREMENT BY 1
        NOCACHE
        NOCYCLE;
    ```

2.  **Enforce Uniqueness on `FULL_IDENTIFIER`:** Although not present in your original DDL, for the logic to work correctly, the `FULL_IDENTIFIER` column must be unique to prevent different systems from accidentally generating the same final ID.
    ```sql
    ALTER TABLE "LICENSE_ADMIN"."LC_ATHX_UNIQUE_IDENTIFIER" 
    ADD CONSTRAINT "UK_FULL_IDENTIFIER" UNIQUE ("FULL_IDENTIFIER");
    ```

---

### 1. Hibernate Entity (`UniqueIdentifier.java`)

This class maps directly to your `LC_ATHX_UNIQUE_IDENTIFIER` table. It uses JPA annotations to define the table, columns, and constraints. Note the use of `@SequenceGenerator` and `@PrePersist`/`@PreUpdate` for automatic population.

`src/main/java/com/example/identifier/entity/UniqueIdentifier.java`
```java
package com.example.identifier.entity;

import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "LC_ATHX_UNIQUE_IDENTIFIER", schema = "LICENSE_ADMIN")
// Using camelCase for fields and mapping snake_case for columns
public class UniqueIdentifier {

    // Note: The column name in the DDL has a typo: "UNIQUE_INDENTIFIER_ID".
    // We must match it exactly.
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "identifierSeqGenerator")
    @SequenceGenerator(name = "identifierSeqGenerator", sequenceName = "LC_IDENTIFIER_VAL_SEQ", schema = "LICENSE_ADMIN", allocationSize = 1)
    @Column(name = "UNIQUE_INDENTIFIER_ID")
    private Long uniqueIdentifierId;

    @Column(name = "SYSTEM_PREFIX", nullable = false, length = 20)
    private String systemPrefix;

    @Column(name = "IDENTIFIER", nullable = false)
    private Long identifier;

    @Column(name = "FULL_IDENTIFIER", nullable = false, length = 200, unique = true)
    private String fullIdentifier;

    @CreationTimestamp
    @Column(name = "CREATE_DATE", nullable = false, updatable = false)
    private LocalDateTime createDate;

    @UpdateTimestamp
    @Column(name = "MODIFY_DATE", nullable = false)
    private LocalDateTime modifyDate;

    // Constructors, Getters, and Setters

    // Default constructor required by JPA
    public UniqueIdentifier() {}

    public UniqueIdentifier(String systemPrefix, Long identifier, String fullIdentifier) {
        this.systemPrefix = systemPrefix;
        this.identifier = identifier;
        this.fullIdentifier = fullIdentifier;
    }

    public Long getUniqueIdentifierId() {
        return uniqueIdentifierId;
    }

    // ... other getters and setters ...

    @Override
    public String toString() {
        return "UniqueIdentifier{" +
                "uniqueIdentifierId=" + uniqueIdentifierId +
                ", systemPrefix='" + systemPrefix + '\'' +
                ", identifier=" + identifier +
                ", fullIdentifier='" + fullIdentifier + '\'' +
                ", createDate=" + createDate +
                ", modifyDate=" + modifyDate +
                '}';
    }
}
```

---

### 2. Spring Data Repository (`UniqueIdentifierRepository.java`)

This interface extends `JpaRepository` to get basic CRUD functionality. Spring Data will automatically provide the implementation. No custom queries are needed for our core logic.

`src/main/java/com/example/identifier/repository/UniqueIdentifierRepository.java`
```java
package com.example.identifier.repository;

import com.example.identifier.entity.UniqueIdentifier;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UniqueIdentifierRepository extends JpaRepository<UniqueIdentifier, Long> {
    // Spring Data provides the necessary methods like save() and findById().
    // A unique constraint on FULL_IDENTIFIER is handled by the DB, which
    // will throw a DataIntegrityViolationException if violated.
}
```

---

### 3. Service Layer (`UniqueIdentifierService.java`)

This is the core of the business logic. It generates the number, ensures uniqueness, and persists the entity. The [`@Transactional`](https://docs.spring.io/spring-framework/docs/current/reference/html/data-access.html#transaction-declarative) annotation is crucial here.

`src/main/java/com/example/identifier/service/UniqueIdentifierService.java`
```java
package com.example.identifier.service;

import com.example.identifier.entity.UniqueIdentifier;
import com.example.identifier.repository.UniqueIdentifierRepository;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

@Service
public class UniqueIdentifierService {

    // Using EntityManager is a standard way to interact with a sequence.
    @PersistenceContext
    private EntityManager entityManager;

    private final UniqueIdentifierRepository repository;

    public UniqueIdentifierService(UniqueIdentifierRepository repository) {
        this.repository = repository;
    }

    /**
     * Generates a new unique identifier for a given system prefix.
     * It fetches the next sequence value, constructs the full identifier,
     * and attempts to save it to the database. It includes a retry mechanism
     * in the extremely rare case of a race condition causing a DB unique key violation.
     *
     * @param systemPrefix The system ID (e.g., "LH", "SAP", "LC").
     * @return The fully generated and stored unique identifier (e.g., "LH-12345").
     * @throws IllegalArgumentException if the system prefix is null or empty.
     */
    @Transactional
    public String generateAndStoreUniqueNumber(String systemPrefix) {
        if (!StringUtils.hasText(systemPrefix)) {
            throw new IllegalArgumentException("System prefix cannot be null or empty.");
        }

        // Retry loop to handle potential race conditions on the unique key.
        int maxAttempts = 3;
        for (int i = 0; i < maxAttempts; i++) {
            try {
                return attemptGeneration(systemPrefix);
            } catch (DataIntegrityViolationException e) {
                // This exception means the 'fullIdentifier' already existed.
                // Log the retry and try again. This is highly unlikely with a DB sequence,
                // but it makes the code ultra-safe.
                System.err.printf("Detected constraint violation for prefix '%s'. Retrying... (Attempt %d/%d)%n", systemPrefix, i + 1, maxAttempts);
                if (i == maxAttempts - 1) {
                    throw new RuntimeException("Failed to generate a unique identifier after " + maxAttempts + " attempts. DB might be in a constrained state.", e);
                }
            }
        }
        throw new IllegalStateException("Should not reach here.");
    }

    @Transactional
    protected String attemptGeneration(String systemPrefix) {
        // 1. Get the next value from the Oracle sequence.
        String nextValSql = "SELECT LC_IDENTIFIER_VAL_SEQ.NEXTVAL FROM DUAL";
        Long nextId = (Long) entityManager.createNativeQuery(nextValSql).getSingleResult();

        // 2. Construct the two parts of our identifier.
        String coreIdentifier = String.valueOf(nextId);
        String fullIdentifier = systemPrefix + "-" + coreIdentifier;

        // 3. Create the entity entity.
        UniqueIdentifier identifierEntity = new UniqueIdentifier(systemPrefix, nextId, fullIdentifier);

        // 4. Save to the database. The `@Transactional` ensures this is part of a transaction.
        repository.save(identifierEntity);

        // 5. Return the generated full identifier.
        return fullIdentifier;
    }
}
```

---

### 4. REST API Controller (`IdentifierController.java`)

This controller exposes an endpoint that third-party systems can call.

`src/main/java/com/example/identifier/controller/IdentifierController.java`
```java
package com.example.identifier.controller;

import com.example.identifier.service.UniqueIdentifierService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/identifiers")
public class IdentifierController {

    private final UniqueIdentifierService identifierService;

    public IdentifierController(UniqueIdentifierService identifierService) {
        this.identifierService = identifierService;
    }

    /**
     * Generates a new unique identifier for a specified system.
     *
     * @param systemPrefix The system prefix to use (e.g., LH, SAP, LC, LH-EDA).
     * @return A response entity containing the generated unique identifier.
     */
    @PostMapping("/generate/{systemPrefix}")
    public ResponseEntity<Map<String, String>> generateUniqueIdentifier(@PathVariable String systemPrefix) {
        try {
            String fullIdentifier = identifierService.generateAndStoreUniqueNumber(systemPrefix);
            
            Map<String, String> response = new HashMap<>();
            response.put("status", "success");
            response.put("message", "Unique identifier generated successfully.");
            response.put("fullIdentifier", fullIdentifier);

            return ResponseEntity.ok(response);

        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("status", "error", "message", e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("status", "error", "message", "An unexpected error occurred: " + e.getMessage()));
        }
    }
}

```

### How to Use the API

Third-party systems can now make a simple `POST` request to the endpoint you've defined. For example, to get a new identifier for the "LH" system:

**Using `curl`:**
```bash
curl -X POST \
  http://localhost:8080/api/v1/identifiers/generate/LH \
  -H 'Content-Type: application/json'
```

**Expected Response:**
```json
{
    "status": "success",
    "message": "Unique identifier generated successfully.",
    "fullIdentifier": "LH-42"
}
```

To get one for "SAP":
```bash
curl -X POST \
  http://localhost:8080/api/v1/identifiers/generate/SAP \
  -H 'Content-Type: application/json'
```

**Expected Response:**
```json
{
    "status": "success",
    "message": "Unique identifier generated successfully.",
    "fullIdentifier": "SAP-43"
}
```