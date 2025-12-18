from universal_launcher import UniversalLauncher

# Create launcher instance
launcher = UniversalLauncher()

# Get blocked domains from configuration
blocked = launcher.config.get('cloud_handshake_management', {}).get('blocked_external_domains', [])

# Test domains
test_domains = [
    'cursor.sh',
    'openai.com',
    'api.openai.com',
    'test.qoder.sh',
    'center.qoder.sh',
    'localhost',
    '127.0.0.1'
]

print("Testing domain matching for all specified domains:")
for domain in test_domains:
    matches = any(launcher._matches_pattern(domain, pattern) for pattern in blocked)
    status = "BLOCKED" if matches else "ALLOWED"
    print(f"  {domain}: {status}")