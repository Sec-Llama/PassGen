# PassGen Pro - Advanced Wordlist Generation Framework

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/security/passgen)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

PassGen Pro is a next-generation wordlist generation framework designed for security professionals, penetration testers, and red team operators. It combines intelligent mutation algorithms, OSINT capabilities, and context-aware pattern generation to create highly effective password lists that outperform traditional tools.

### Key Differentiators

- **Intelligent Mutation Engine**: Multi-level transformation system with context-aware mutations
- **OSINT Integration**: Deep web scraping with parallel processing and intelligent word extraction
- **Memory-Safe Architecture**: Prevents combinatorial explosion through smart limiting algorithms
- **Pattern-Based Generation**: Advanced mask system superior to crunch with more pattern options
- **Likelihood Scoring**: Passwords ranked by probability of real-world usage
- **Production-Grade**: Comprehensive error handling, type safety, and robust validation

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Features](#core-features)
- [Usage Examples](#usage-examples)
- [Pattern Syntax Reference](#pattern-syntax-reference)
- [Advanced Techniques](#advanced-techniques)
- [Performance Benchmarks](#performance-benchmarks)
- [Comparison Matrix](#comparison-matrix)
- [Technical Architecture](#technical-architecture)
- [Contributing](#contributing)

## Installation

### Requirements

- Python 3.7 or higher
- Optional: requests, beautifulsoup4 (for web scraping features)

### Basic Installation

```bash
# Clone repository
git clone https://github.com/Sec-Llama/PassGen.git
cd passgen-pro

# Install optional dependencies for full functionality
pip install requests beautifulsoup4

# Verify installation
python PassGen.py -h
```

### Minimal Installation

The tool works without external dependencies, though web scraping will be disabled:

```bash
# Run without dependencies (core features only)
python PassGen.py -w admin root -o wordlist.txt
```

## Quick Start

### Basic Generation

```bash
# Generate from base words
python PassGen.py -w admin password root -o wordlist.txt

# Add intelligent mutations
python PassGen.py -w admin password --leet -o mutated.txt

# Include date patterns and keyboard walks
python PassGen.py -w company --dates --keyboard -o enhanced.txt
```

### OSINT Mode

```bash
# Scrape target website
python PassGen.py -u https://target.com -d 2 -o osint.txt

# Multiple URLs with parallel processing
python PassGen.py -u https://target.com https://target.org --threads 8 -o multi.txt
```

### Pattern Generation

```bash
# Custom patterns (superior to crunch)
python PassGen.py -p "admin%%%%" "root@@@@" -o patterns.txt

# Complex patterns with multiple character classes
python PassGen.py -p "Admin%%@@^^" "user,,,,%%%%" -o complex_patterns.txt
```

## Core Features

### 1. Mutation Engine

The mutation engine operates on three levels:

**Level 1 - Basic Mutations**
- Case transformations (lower, upper, capitalize, title)
- Common suffix additions (123, !, @, current year)
- Standard prefix additions (admin, user, test)

**Level 2 - Advanced Mutations**
- Leetspeak transformations with controlled variants
- String reversal and doubling
- Vowel removal algorithms
- Context-aware combinations

**Level 3 - Extreme Mutations**
- Full combinatorial prefix/suffix application
- Character substitution matrices
- Pattern-based transformations

### 2. OSINT Capabilities

**Web Scraping Features**
- Multi-depth crawling with domain restriction
- Parallel URL processing with ThreadPoolExecutor
- Intelligent word extraction from:
  - Page content
  - Meta tags
  - Email addresses
  - HTML comments
  - JavaScript variables

**Data Extraction**
- Automatic email parsing and username extraction
- Domain name analysis
- Keyword density analysis
- Pattern recognition for common formats

### 3. Pattern Generation System

Advanced pattern mask system with the following character classes:

| Symbol | Character Class | Example |
|--------|----------------|---------|
| `@` | Lowercase letter | `@@@` → `abc` |
| `,` | Uppercase letter | `,,,` → `XYZ` |
| `%` | Digit | `%%%` → `123` |
| `^` | Special character | `^^^` → `!@#` |
| `?` | Alphanumeric | `???` → `a1B` |
| `d` | Digit (alternate) | `ddd` → `456` |
| `l` | Lowercase (alternate) | `lll` → `xyz` |
| `u` | Uppercase (alternate) | `uuu` → `ABC` |
| `s` | Special (alternate) | `sss` → `$%&` |

### 4. Name-Based Generation

Intelligent combination of personal information:

```bash
# Full name combinations with company integration
python PassGen.py --first john jane --last doe smith --company acme -o names.txt
```

Generates patterns like:
- `johndoe`, `doejohn`, `john.doe`, `john_doe`
- `jdoe`, `johnd`, `j.doe`, `john@acme`
- `johndoe2024`, `jdoe123`, `johnacme!`

### 5. Filtering and Optimization

**Length Filters**
```bash
python PassGen.py -w base --min 8 --max 16 -o filtered.txt
```

**Complexity Requirements**
```bash
python PassGen.py -w base --upper --lower --digit --special -o complex.txt
```

**Likelihood Scoring**
```bash
python PassGen.py -w base --smart -o sorted_by_probability.txt
```

## Usage Examples

### Scenario 1: Corporate Penetration Test

```bash
# Gather intelligence from corporate website and generate targeted list
python PassGen.py \
  -u https://corporate-target.com -d 3 \
  --company CorpName \
  --first john michael sarah \
  --last smith johnson williams \
  --dates --start-year 2020 \
  --min 8 --max 20 \
  --upper --digit \
  --smart --stats \
  -o corporate_audit.txt
```

### Scenario 2: Social Engineering Campaign

```bash
# Generate passwords based on OSINT data
python PassGen.py \
  -i osint_keywords.txt \
  -u https://target-social.com \
  --leet \
  --dates \
  -p "Target%%%%" "target@@@@" \
  --smart \
  -o social_eng.txt
```

### Scenario 3: Password Policy Testing

```bash
# Generate compliant passwords for policy testing
python PassGen.py \
  -w password pass \
  --min 12 --max 20 \
  --upper --lower --digit --special \
  -p "Pass%%%%@@@@^^^^" \
  --no-combo \
  -o policy_test.txt
```

### Scenario 4: Wireless Network Auditing

```bash
# Common router/WiFi passwords
python PassGen.py \
  -w admin password wifi network \
  --keyboard \
  -p "WiFi%%%%" "Network@@@@" \
  --dates --start-year 2020 \
  --leet \
  -o wifi_audit.txt
```

## Pattern Syntax Reference

### Basic Patterns

```bash
# Fixed text with patterns
"Admin%%%%" → Admin0000 to Admin9999

# Multiple character classes
"Pass@@%%^^" → Passab12!@ 

# Pure patterns
"@@@@@@@@" → 8 lowercase letters
```

### Advanced Pattern Combinations

```bash
# Company-based patterns
python PassGen.py -p "Company%%@@" "COMPANY%%%%" "company_%%_@@"

# Date-based patterns
python PassGen.py -p "user%%%%-%%-%%" "pass%%/%%/%%%%"

# Complex multi-class
python PassGen.py -p "@@@@%%%%^^^^" ",,,ddddsss"
```

## Advanced Techniques

### 1. Custom Rule Files

Create a rules file for advanced transformations:

```text
# rules.txt
append:2024
prepend:admin_
replace:a,@
replace:e,3
```

```bash
python PassGen.py -w base --rules rules.txt -o custom_rules.txt
```

### 2. Incremental Generation

For large-scale operations, use incremental generation:

```bash
# Stage 1: Base words
python PassGen.py -w admin user -o stage1.txt

# Stage 2: Add mutations
python PassGen.py -i stage1.txt --leet --dates -o stage2.txt

# Stage 3: Apply patterns
python PassGen.py -i stage2.txt -p "%%%%@@@@" -o final.txt
```

### 3. Targeted Wordlist Optimization

```bash
# Analyze existing passwords for patterns
python PassGen.py -i cracked_passwords.txt \
  --analyze \
  --generate-similar \
  -o optimized.txt
```

### 4. Multi-Vector Attack Lists

```bash
# Combine multiple attack vectors
python PassGen.py \
  -w admin root \
  -u https://target.com \
  --first alice bob --last smith jones \
  --company target \
  -p "Target%%%%" "admin@@@@" \
  --dates --keyboard --leet \
  --min 8 --max 24 \
  --smart --threads 10 \
  -o multi_vector.txt
```

## Performance Benchmarks

### Generation Speed

| Operation | Words/Second | Memory Usage |
|-----------|-------------|--------------|
| Basic mutations | ~50,000 | <100MB |
| Leetspeak (Level 2) | ~20,000 | <200MB |
| Combinations (2-word) | ~30,000 | <150MB |
| Pattern generation | ~100,000 | <50MB |
| Web scraping | ~500 URLs/min | <300MB |

### Scalability Tests

| Input Size | Generation Time | Output Size | Memory Peak |
|------------|----------------|-------------|-------------|
| 100 base words | <1 second | ~10,000 passwords | 50MB |
| 1,000 base words | ~5 seconds | ~100,000 passwords | 200MB |
| 10,000 base words | ~30 seconds | ~500,000 passwords | 500MB |
| Web scrape (depth=3) | ~60 seconds | ~50,000 passwords | 300MB |

## Comparison Matrix

| Feature | PassGen Pro | Crunch | CeWL | CUPP | JtR/Hashcat |
|---------|------------|--------|------|------|-------------|
| Pattern masks | Advanced | Basic | No | No | Yes |
| Web scraping | Multi-depth | No | Yes | No | No |
| Name combinations | Intelligent | No | No | Basic | Limited |
| Leetspeak | Multi-level | No | No | Basic | Rules |
| Memory safety | Enforced | No | Yes | Yes | Yes |
| Parallel processing | Yes | No | No | No | Yes |
| Likelihood scoring | Yes | No | No | No | No |
| OSINT integration | Native | No | Basic | No | No |
| Context awareness | High | None | Medium | Low | Medium |
| Production ready | Yes | Yes | Yes | No | Yes |

## Technical Architecture

### Class Structure

```
PassGen Pro
├── PassGenPro (Orchestrator)
│   ├── Configuration management
│   ├── Pipeline coordination
│   └── Output handling
├── PasswordGenerator (Core Engine)
│   ├── Mutation algorithms
│   ├── Pattern generation
│   └── Combination logic
└── WebScraper (OSINT Module)
    ├── Parallel fetching
    ├── Content extraction
    └── Pattern recognition
```

### Memory Management

- **Smart Limiting**: Automatic caps on combinatorial operations
- **Streaming Processing**: Large files processed in chunks
- **Garbage Collection**: Explicit cleanup after large operations
- **Set Deduplication**: Automatic duplicate removal at each stage

### Threading Model

- **ThreadPoolExecutor**: For parallel web scraping
- **Configurable Workers**: Default 4, max 10
- **Timeout Protection**: 30-second timeout per URL
- **Error Isolation**: Failed threads don't affect others

## Security Considerations

### Operational Security

1. **Traffic Patterns**: Web scraping may be detected. Use `--threads 1` for stealth
2. **Rate Limiting**: Implement delays between requests when targeting production sites
3. **User-Agent Rotation**: Modify source to rotate user agents if needed
4. **Proxy Support**: Use system proxy settings or modify for SOCKS/HTTP proxy

### Legal Compliance

- Only use against systems you have authorization to test
- Respect robots.txt when web scraping
- Consider rate limiting to avoid DoS conditions
- Store generated wordlists securely

## Troubleshooting

### Common Issues

**Issue**: Web scraping not working
```bash
# Solution: Install dependencies
pip install requests beautifulsoup4
```

**Issue**: Memory error with large inputs
```bash
# Solution: Use filters and limits
python PassGen.py -w base --max-combo 1 --no-leet -o limited.txt
```

**Issue**: Slow generation
```bash
# Solution: Disable smart ordering
python PassGen.py -w base --no-smart -o fast.txt
```

## Contributing

Contributions are welcome. Please ensure:

1. Code follows PEP 8 style guidelines
2. Type hints are used for all functions
3. Error handling is comprehensive
4. Changes include relevant documentation
5. Performance impact is measured

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool is intended for authorized security testing only. Users are responsible for complying with all applicable laws and regulations. The authors assume no liability for misuse or damage caused by this software.

## Author

Security Research Team  
Version: 3.0.0  
Last Updated: 2024
