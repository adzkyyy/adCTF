# adCTF Node

This is an Attack & Defense CTF node that manages challenge services and health checking.

## Challenge Creation Requirements

### 1. Challenge Files Structure

Each challenge must be created with the following structure:

```
{repo}/services/{challenge_name}/
├── docker-compose.yml    # Main compose file for the challenge
├── Dockerfile           # Container definition
├── flag.txt            # Flag file (must be at /flag.txt in container)
└── src/                # Challenge source code
    ├── main.py         # Main application
    ├── requirements.txt # Dependencies
    └── ...             # Other source files
```

**Requirements:**
- Must have `docker-compose.yml` and `Dockerfile` in the main directory
- Should be runnable with `docker compose up`
- Flag must be placed at root directory as `/flag.txt` inside the container
- Challenge must be a functional service with working features
- Must contain exploitable vulnerabilities that can be patched
- Service functionality must be verifiable (health checkable)

**Integration Steps:**
1. **Add to main services configuration**: Update `/services/docker-compose.yml` to include your challenge container
2. **Configure receiver endpoint**: 
   - Update `/receiver/main.py` to register the challenge endpoint

### 2. Checker Script Requirements

Each challenge requires a checker script at `{repo}/receiver/challenges/{challenge_name}.py`

**Structure:**
```python
from Challenge import Challenge

class ChallengeNameChecker(Challenge):
    def __init__(self):
        super().__init__()
        # Take a look at receiver/challenges/Notes.py for example
        
    def check(self):
        """
        Check if the challenge service is still functional
        
        Returns:
            bool: True if service is working, False otherwise
        """
        # Implement functionality check here
        # Example: HTTP request to verify service response
        # Example: Database connection test
        # Example: API endpoint verification
        
        try:
            # Your checking logic here
            return True
        except Exception as e:
            print(f"Check failed: {e}")
            return False
```

**Requirements:**
- Inherit from the `Challenge` base class (see existing examples in the directory)
- Implement the `check(self)` method to verify service functionality
- Must return `True` if service is working properly, `False` otherwise
- Should test core functionality, not just port availability
- Handle exceptions gracefully

### 3. Configuration Updates

After creating your challenge, you need to integrate it into the system:

#### A. Update Services Configuration
Add your challenge to `/services/docker-compose.yml`:
```yaml
services:
  your_challenge_name:
    build: ./your_challenge_name
    ports:
      - "8080:8080"  # Adjust ports as needed
    networks:
      - ctf_network
    restart: unless-stopped
```

#### B. Update Receiver Configuration
1. **Add to `/receiver/config.py`**: Register your challenge configuration
```python
CHALLENGES = {
    'your_challenge_name': {
        'host': 'localhost',
        'port': 8080,
        'enabled': True
    }
}
```

2. **Update `/receiver/main.py`**: Add endpoint registration for your challenge
```python
from challenges.your_challenge_name import YourChallengeNameChecker

# Add to challenge initialization
challenges['your_challenge_name'] = YourChallengeNameChecker()
```

## How to Run

```bash
sudo python3 starter.py
```

## Directory Structure

- `/services/` - Contains all challenge services
- `/receiver/challenges/` - Contains checker scripts for each challenge
- `/receiver/flags/` - Flag storage
- `/utils/` - Utility scripts and configurations
