
```mermaid
architecture-beta
    group aws(cloud)[AWS]

    service web(internet)[User]
    service frontend(server)[Frontend] in aws
    service backend(server)[Backend] in aws
    service database(database)[Database] in aws
    service storage(disk)[Storage] in aws

    web:L --> R:frontend
    frontend:L --> R:backend
    backend:T --> B:database
    backend:T --> L:storage
    web:L --> R:storage
```
