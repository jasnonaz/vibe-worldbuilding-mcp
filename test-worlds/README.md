# Test Worlds Directory

This directory contains isolated test environments for the vibe-worldbuilding system.

## Structure

- **unit/**: Test worlds for individual feature validation
- **integration/**: End-to-end test scenarios
- **performance/**: Load testing and performance benchmarks

## Usage

Test worlds are automatically created and cleaned up by the test suite. This directory is git-ignored to prevent test artifacts from being committed.

## Manual Testing

You can manually create test worlds here for development:

```bash
# Run tests in this directory
python ../test_e2e_simple.py --base-dir ./test-worlds --verbose --cleanup

# Create a development world
python -c "
import sys; sys.path.insert(0, '..')
from vibe_worldbuilding.tools.world import handle_world_tool
import asyncio
result = asyncio.run(handle_world_tool('instantiate_world', {
    'world_name': 'dev-test',
    'world_content': '# Dev World\n\nA world for manual testing.',
    'base_directory': './test-worlds'
}))
print(result[0].text)
"
```

## Cleanup

To clean all test worlds:
```bash
rm -rf test-worlds/*/
```