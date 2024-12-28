# 5. Advanced Features

- **Custom Headers:** Include headers like `ngrok-skip-browser-warning` to bypass specific checks.
- **Multi-Server Support:** Switch between `https://example.com` and `https://example.org` seamlessly.

### Load Balancing (Future Implementation)
```mermaid
graph LR
    A[Client Request] --> B[Load Balancer]
    B -->|Route to| C[example.com]
    B -->|Route to| D[example.org]
```
