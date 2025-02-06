# Load Testing with Locust

This directory contains load tests for the Multiverse Market API using Locust.

## Running with Docker (Recommended)

The load tests are integrated into the main docker-compose setup with a dedicated profile. To run the tests:

1. Make sure you're in the root directory of the project
2. Start the load testing environment:
```bash
make docker/loadtest
```

This will start:
- The main application stack (API, database, Redis)
- A Locust master node
- Two Locust worker nodes

3. Open http://localhost:8089 in your browser
4. Enter the test parameters:
   - Number of users: Start with 10-50 for initial testing
   - Spawn rate: 1-5 users per second
   - The host URL is automatically configured

Useful commands:
```bash
# View Locust logs
make docker/loadtest/logs

# Stop the load testing environment
make docker/loadtest/stop
```

## Running Locally (Alternative)

If you prefer to run Locust directly on your machine:

1. Install Locust:
```bash
pip install locust
```

2. Make sure your API server is running
3. From this directory, run:
```bash
locust -f locustfile.py
```
4. Open http://localhost:8089 in your browser
5. Enter the parameters:
   - Number of users: Start with 10-50 for initial testing
   - Spawn rate: 1-5 users per second
   - Host: Your API URL (e.g., http://localhost:8000)

## What's Being Tested

The load tests simulate realistic user behavior with different frequencies:

### High Frequency Operations (3-4x weight)
- Listing all universes
- Listing items (with and without universe filters)

### Medium Frequency Operations (2x weight)
- Getting user details
- Getting user trade history

### Low Frequency Operations (1x weight)
- Currency exchange between universes
- Buying items

## Test Data

The tests use the seeded test data from the database:
- Users: IDs 1-3
- Universes: IDs 1-3
- Items: IDs 1-3

## Interpreting Results

Locust provides real-time metrics including:
- Request count and failure rates
- Response times (min, max, median, 95th percentile)
- Requests per second
- Number of users

Watch for:
1. Response times staying consistent under load
2. No unexpected errors
3. Success rate remaining high

## Common Issues

1. If you see many failed requests:
   - Check if the API server is running
   - Verify the correct host URL
   - Ensure the test data exists in the database

2. If response times are too high:
   - Check database query performance
   - Verify Redis cache is working
   - Consider API optimizations

## Docker-specific Troubleshooting

1. If the Locust web interface isn't accessible:
   - Check if all containers are running: `make docker/ps`
   - View Locust logs: `make docker/loadtest/logs`
   - Ensure port 8089 is not in use by another application

2. If workers aren't connecting:
   - Check the logs: `make docker/loadtest/logs`
   - Verify network connectivity between containers