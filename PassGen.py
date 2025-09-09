#!/usr/bin/env python3
"""
PassGen Pro - Next-Generation Intelligent Wordlist Generator
Version: 3.0.0
Author: Michael Dahan
License: MIT
"""

import argparse
import itertools
import json
import os
import re
import string
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Set, List, Dict, Optional, Any, Tuple
from urllib.parse import urlparse

# Optional imports with graceful fallback
try:
    import requests
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False
    print("[!] Warning: requests/beautifulsoup4 not installed. Web scraping disabled.")
    print("[!] Install with: pip install requests beautifulsoup4")


class PasswordGenerator:
    """Core password generation engine with intelligent mutations"""
    
    # Common password patterns and suffixes
    COMMON_SUFFIXES = [
        '1', '12', '123', '1234', '12345', '123456',
        '!', '@', '#', '$', '!!', '!@#', '123!',
        '00', '01', '11', '22', '69', '77', '88', '99',
        '2020', '2021', '2022', '2023', '2024', '2025',
        '_', '.', '-'
    ]
    
    COMMON_PREFIXES = [
        'admin', 'user', 'test', 'demo', 'guest',
        'root', 'super', 'master', 'pass', 'pwd'
    ]
    
    # Leetspeak mappings (conservative to avoid explosion)
    LEET_MAP = {
        'a': ['@', '4'], 'e': ['3'], 'i': ['1', '!'],
        'o': ['0'], 's': ['5', '$'], 't': ['7'],
        'l': ['1'], 'g': ['9']
    }
    
    # Keyboard walk patterns
    KEYBOARD_WALKS = [
        'qwerty', 'qwertyuiop', 'asdfgh', 'asdfghjkl',
        'zxcvbn', 'zxcvbnm', '123456', '1234567890',
        'qazwsx', 'qazxsw', 'qweasd', 'qweasdzxc',
        '1qaz2wsx', '1qaz2wsx3edc', 'zaq1xsw2',
        'password', 'passw0rd', 'p@ssw0rd'
    ]
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.stats = defaultdict(int)
        
    def mutate_word(self, word: str, level: int = 1) -> Set[str]:
        """
        Apply intelligent mutations to a word
        Level 1: Basic (case, simple suffixes)
        Level 2: Advanced (leetspeak, combinations)
        Level 3: Extreme (all variations)
        """
        mutations = {word}
        
        if not word:
            return mutations
            
        # Level 1: Basic mutations
        mutations.add(word.lower())
        mutations.add(word.upper())
        mutations.add(word.capitalize())
        mutations.add(word.title())
        
        # Add common suffixes
        for suffix in self.COMMON_SUFFIXES[:10 if level == 1 else None]:
            mutations.add(word + suffix)
            mutations.add(word.capitalize() + suffix)
            
        # Add year patterns
        current_year = datetime.now().year
        for year_offset in range(-2, 3):
            year = str(current_year + year_offset)
            mutations.add(word + year)
            mutations.add(word + year[-2:])
            
        if level >= 2:
            # Level 2: Advanced mutations
            # Reverse
            mutations.add(word[::-1])
            
            # Double
            if len(word) <= 8:
                mutations.add(word * 2)
                
            # Remove vowels
            no_vowels = ''.join(c for c in word if c.lower() not in 'aeiou')
            if no_vowels and len(no_vowels) >= 3:
                mutations.add(no_vowels)
                
            # Leetspeak (limited to prevent explosion)
            if self.config.get('leet', False):
                leet_variants = self._apply_leetspeak(word, max_variants=5)
                mutations.update(leet_variants)
                
        if level >= 3:
            # Level 3: Extreme mutations
            # All prefix combinations
            for prefix in self.COMMON_PREFIXES:
                if not word.lower().startswith(prefix):
                    mutations.add(prefix + word)
                    mutations.add(prefix + '_' + word)
                    
            # Character substitution
            mutations.add(word.replace('a', '@').replace('s', '$'))
            mutations.add(word.replace('e', '3').replace('o', '0'))
            
        return mutations
    
    def _apply_leetspeak(self, word: str, max_variants: int = 5) -> Set[str]:
        """Apply leetspeak transformations with controlled explosion"""
        variants = {word}
        
        for char, replacements in self.LEET_MAP.items():
            if char in word.lower():
                new_variants = set()
                for variant in list(variants)[:max_variants]:
                    for replacement in replacements:
                        new_variant = variant.replace(char, replacement)
                        new_variant2 = variant.replace(char.upper(), replacement)
                        new_variants.add(new_variant)
                        new_variants.add(new_variant2)
                        
                variants.update(new_variants)
                if len(variants) > max_variants * 2:
                    break
                    
        return set(list(variants)[:max_variants * 2])
    
    def generate_combinations(self, words: List[str], max_length: int = 32) -> Set[str]:
        """Generate intelligent word combinations"""
        combinations = set()
        
        # Limit words to prevent explosion
        words = words[:30]
        
        # Two-word combinations
        for w1, w2 in itertools.combinations(words, 2):
            if len(w1) + len(w2) <= max_length:
                combinations.add(w1 + w2)
                combinations.add(w2 + w1)
                combinations.add(w1.capitalize() + w2.capitalize())
                combinations.add(w1 + '_' + w2)
                combinations.add(w1 + '.' + w2)
                combinations.add(w1 + '-' + w2)
                
        # Three-word combinations (very limited)
        if len(words) >= 3:
            for combo in itertools.combinations(words[:10], 3):
                combined = ''.join(combo)
                if len(combined) <= max_length:
                    combinations.add(combined)
                    combinations.add(''.join(c.capitalize() for c in combo))
                    
        return combinations
    
    def generate_from_pattern(self, pattern: str, limit: int = 1000) -> Set[str]:
        """Generate passwords from pattern masks"""
        results = set()
        
        # Pattern character mappings
        mappings = {
            '@': string.ascii_lowercase,
            ',': string.ascii_uppercase,
            '%': string.digits,
            '^': '!@#$%^&*',
            '?': string.ascii_letters,
            'd': string.digits,
            'l': string.ascii_lowercase,
            'u': string.ascii_uppercase,
            's': '!@#$%^&*()_+-='
        }
        
        def _generate(pattern: str, current: str = ''):
            if len(results) >= limit:
                return
                
            if not pattern:
                results.add(current)
                return
                
            char = pattern[0]
            remaining = pattern[1:]
            
            if char in mappings:
                # Limit characters to prevent explosion
                chars_to_use = mappings[char][:5] if len(mappings[char]) > 5 else mappings[char]
                for replacement in chars_to_use:
                    _generate(remaining, current + replacement)
            else:
                _generate(remaining, current + char)
                
        _generate(pattern)
        return results
    
    def generate_keyboard_walks(self) -> Set[str]:
        """Generate keyboard walk patterns"""
        walks = set(self.KEYBOARD_WALKS)
        
        # Add reverse walks
        walks.update(w[::-1] for w in self.KEYBOARD_WALKS)
        
        # Add capitalized versions
        walks.update(w.capitalize() for w in walks.copy())
        walks.update(w.upper() for w in walks.copy())
        
        return walks
    
    def generate_dates(self, start_year: int = 2015, end_year: Optional[int] = None) -> Set[str]:
        """Generate date-based patterns"""
        dates = set()
        
        if not end_year:
            end_year = datetime.now().year + 2
            
        # Years
        for year in range(start_year, end_year):
            dates.add(str(year))
            dates.add(str(year)[-2:])
            
        # Common date patterns
        dates.update(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'])
        dates.update(['123', '321', '111', '222', '333', '444', '555', '666', '777', '888', '999', '000'])
        
        # Birth years (common range)
        for year in range(1970, 2010):
            dates.add(str(year))
            dates.add(str(year)[-2:])
            
        return dates


class WebScraper:
    """Web scraping module for OSINT gathering"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = None
        if WEB_SCRAPING_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
    
    def scrape_url(self, url: str, depth: int = 1) -> Set[str]:
        """Scrape URL for words with depth control"""
        if not WEB_SCRAPING_AVAILABLE:
            return set()
            
        words = set()
        visited = set()
        
        def _scrape_page(page_url: str, current_depth: int):
            if current_depth > depth or page_url in visited:
                return
                
            visited.add(page_url)
            
            try:
                response = self.session.get(page_url, timeout=5)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                
                # Extract words (3+ chars, alphanumeric)
                found_words = re.findall(r'\b[a-zA-Z0-9]{3,20}\b', text)
                words.update(w.lower() for w in found_words)
                
                # Extract emails and usernames
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
                for email in emails:
                    username = email.split('@')[0]
                    words.add(username.lower())
                    
                # Extract from meta tags
                for meta in soup.find_all('meta'):
                    content = meta.get('content', '')
                    if content:
                        meta_words = re.findall(r'\b[a-zA-Z0-9]{3,20}\b', content)
                        words.update(w.lower() for w in meta_words)
                        
                # Follow internal links if depth allows
                if current_depth < depth:
                    base_domain = urlparse(page_url).netloc
                    links = soup.find_all('a', href=True)
                    
                    for link in links[:10]:  # Limit links per page
                        href = link['href']
                        if href.startswith('http'):
                            if urlparse(href).netloc == base_domain:
                                _scrape_page(href, current_depth + 1)
                                
            except Exception as e:
                if self.config.get('verbose'):
                    print(f"[!] Error scraping {page_url}: {str(e)[:50]}")
                    
        _scrape_page(url, 0)
        return words
    
    def scrape_urls_parallel(self, urls: List[str], depth: int = 1) -> Set[str]:
        """Scrape multiple URLs in parallel"""
        if not WEB_SCRAPING_AVAILABLE:
            return set()
            
        all_words = set()
        max_workers = min(len(urls), self.config.get('threads', 4))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.scrape_url, url, depth): url for url in urls}
            
            for future in as_completed(futures):
                try:
                    words = future.result(timeout=30)
                    all_words.update(words)
                except Exception as e:
                    if self.config.get('verbose'):
                        print(f"[!] Failed to scrape {futures[future]}: {str(e)[:50]}")
                        
        return all_words


class PassGenPro:
    """Main wordlist generator orchestrator"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.generator = PasswordGenerator(config)
        self.scraper = WebScraper(config)
        self.base_words = set()
        self.wordlist = set()
        self.stats = {
            'base_words': 0,
            'mutations': 0,
            'combinations': 0,
            'total': 0,
            'filtered': 0
        }
    
    def collect_base_words(self) -> None:
        """Collect base words from all configured sources"""
        
        # From command line words
        if self.config.get('words'):
            self.base_words.update(w.lower() for w in self.config['words'])
            
        # From input file
        if self.config.get('input_file'):
            try:
                with open(self.config['input_file'], 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        word = line.strip()
                        if word and 3 <= len(word) <= 20:
                            self.base_words.add(word.lower())
            except Exception as e:
                print(f"[!] Error reading input file: {e}")
                
        # From web scraping
        if self.config.get('urls') and WEB_SCRAPING_AVAILABLE:
            print("[*] Scraping websites...")
            scraped = self.scraper.scrape_urls_parallel(
                self.config['urls'],
                self.config.get('depth', 1)
            )
            self.base_words.update(scraped)
            
        # From names
        if self.config.get('first_names') or self.config.get('last_names'):
            names = []
            names.extend(self.config.get('first_names', []))
            names.extend(self.config.get('last_names', []))
            self.base_words.update(n.lower() for n in names)
            
        # Add company name
        if self.config.get('company'):
            self.base_words.add(self.config['company'].lower())
            
        self.stats['base_words'] = len(self.base_words)
    
    def generate_from_names(self) -> Set[str]:
        """Generate passwords from name combinations"""
        passwords = set()
        
        first_names = [n.lower() for n in self.config.get('first_names', [])]
        last_names = [n.lower() for n in self.config.get('last_names', [])]
        company = self.config.get('company', '').lower()
        
        for first in first_names:
            for last in last_names:
                # Basic combinations
                passwords.add(first + last)
                passwords.add(last + first)
                passwords.add(first + '.' + last)
                passwords.add(first + '_' + last)
                passwords.add(first[0] + last)
                passwords.add(first + last[0])
                
                # With company
                if company:
                    passwords.add(first + company)
                    passwords.add(first + '@' + company)
                    passwords.add(first[0] + last[0] + company)
                    
                # With common suffixes
                for suffix in ['123', '2024', '!', '1']:
                    passwords.add(first + last + suffix)
                    passwords.add(first[0] + last + suffix)
                    
        return passwords
    
    def apply_filters(self) -> None:
        """Apply length and complexity filters"""
        filtered = set()
        min_len = self.config.get('min_length', 1)
        max_len = self.config.get('max_length', 128)
        
        for password in self.wordlist:
            # Length filter
            if not (min_len <= len(password) <= max_len):
                continue
                
            # Complexity filters
            if self.config.get('require_upper') and not any(c.isupper() for c in password):
                continue
            if self.config.get('require_lower') and not any(c.islower() for c in password):
                continue
            if self.config.get('require_digit') and not any(c.isdigit() for c in password):
                continue
            if self.config.get('require_special'):
                if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
                    continue
                    
            filtered.add(password)
            
        self.stats['filtered'] = len(self.wordlist) - len(filtered)
        self.wordlist = filtered
    
    def sort_by_likelihood(self) -> List[str]:
        """Sort passwords by likelihood score"""
        scored = []
        
        for password in self.wordlist:
            score = 0
            
            # Optimal length (8-12 chars)
            if 8 <= len(password) <= 12:
                score += 20
            elif 6 <= len(password) <= 16:
                score += 10
                
            # Contains recent year
            for year in ['2023', '2024', '2025']:
                if year in password:
                    score += 15
                    break
                    
            # Common patterns
            if any(p in password.lower() for p in ['admin', 'user', 'pass', '123', 'test']):
                score += 10
                
            # Mixed case
            if any(c.isupper() for c in password) and any(c.islower() for c in password):
                score += 5
                
            # Has numbers at end
            if password and password[-1].isdigit():
                score += 8
                
            # Contains base word
            for word in list(self.base_words)[:20]:
                if len(word) >= 4 and word in password.lower():
                    score += 25
                    break
                    
            scored.append((score, password))
            
        # Sort by score (descending) then alphabetically
        scored.sort(key=lambda x: (-x[0], x[1]))
        return [pwd for score, pwd in scored]
    
    def generate(self) -> List[str]:
        """Main generation pipeline"""
        print("[*] PassGen Pro - Starting generation...")
        start_time = time.time()
        
        # Collect base words
        print("[*] Collecting base words...")
        self.collect_base_words()
        print(f"[+] Collected {len(self.base_words)} base words")
        
        if not self.base_words and not self.config.get('keyboard_walks') and not self.config.get('patterns'):
            print("[!] No base words found. Add words with -w or other input sources.")
            return []
        
        # Apply mutations
        if self.base_words:
            print("[*] Applying mutations...")
            mutation_level = 2 if self.config.get('leet') else 1
            
            for word in self.base_words:
                mutations = self.generator.mutate_word(word, level=mutation_level)
                self.wordlist.update(mutations)
                self.stats['mutations'] += len(mutations)
        
        # Generate combinations
        if self.config.get('combinations', True) and len(self.base_words) > 1:
            print("[*] Generating combinations...")
            max_length = self.config.get('max_length', 32)
            combinations = self.generator.generate_combinations(
                list(self.base_words)[:50],
                max_length
            )
            self.wordlist.update(combinations)
            self.stats['combinations'] = len(combinations)
        
        # Add date patterns
        if self.config.get('dates'):
            print("[*] Adding date patterns...")
            dates = self.generator.generate_dates(
                self.config.get('start_year', 2015),
                self.config.get('end_year')
            )
            
            # Add dates standalone
            self.wordlist.update(dates)
            
            # Combine with base words (limited)
            for word in list(self.base_words)[:20]:
                for date in list(dates)[:20]:
                    self.wordlist.add(word + date)
                    self.wordlist.add(date + word)
        
        # Add keyboard walks
        if self.config.get('keyboard_walks'):
            print("[*] Adding keyboard patterns...")
            walks = self.generator.generate_keyboard_walks()
            self.wordlist.update(walks)
        
        # Generate from patterns
        if self.config.get('patterns'):
            print("[*] Generating from patterns...")
            for pattern in self.config['patterns']:
                pattern_passwords = self.generator.generate_from_pattern(pattern)
                self.wordlist.update(pattern_passwords)
        
        # Generate from names
        if self.config.get('first_names') and self.config.get('last_names'):
            print("[*] Generating name combinations...")
            name_passwords = self.generate_from_names()
            self.wordlist.update(name_passwords)
        
        # Apply filters
        print("[*] Applying filters...")
        self.apply_filters()
        
        # Sort by likelihood if requested
        if self.config.get('smart_order'):
            print("[*] Sorting by likelihood...")
            result = self.sort_by_likelihood()
        else:
            result = list(self.wordlist)
            
        self.stats['total'] = len(result)
        
        elapsed = time.time() - start_time
        print(f"[+] Generation complete in {elapsed:.2f} seconds")
        print(f"[+] Generated {self.stats['total']} unique passwords")
        
        return result
    
    def save(self, passwords: List[str], output_file: str) -> None:
        """Save passwords to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for password in passwords:
                    f.write(password + '\n')
            print(f"[+] Saved to {output_file}")
            
            # Save statistics if requested
            if self.config.get('save_stats'):
                stats_file = output_file.replace('.txt', '_stats.json')
                with open(stats_file, 'w') as f:
                    json.dump(self.stats, f, indent=2)
                print(f"[+] Statistics saved to {stats_file}")
                
        except Exception as e:
            print(f"[!] Error saving file: {e}")
            sys.exit(1)
    
    def print_stats(self) -> None:
        """Print generation statistics"""
        print("\n" + "="*50)
        print("GENERATION STATISTICS")
        print("="*50)
        print(f"Base words:      {self.stats['base_words']:,}")
        print(f"Mutations:       {self.stats['mutations']:,}")
        print(f"Combinations:    {self.stats['combinations']:,}")
        print(f"Filtered out:    {self.stats['filtered']:,}")
        print(f"Total generated: {self.stats['total']:,}")
        
        if self.wordlist:
            # Length distribution
            lengths = Counter(len(p) for p in list(self.wordlist)[:1000])
            common_lengths = lengths.most_common(5)
            print(f"Common lengths:  {', '.join(f'{l}:{c}' for l, c in common_lengths)}")
        print("="*50)


def main():
    parser = argparse.ArgumentParser(
        description='PassGen Pro - Intelligent Wordlist Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  Basic generation:
    %(prog)s -w admin root password -o wordlist.txt
    
  Web scraping + mutations:
    %(prog)s -u https://example.com --leet -o wordlist.txt
    
  Name-based generation:
    %(prog)s --first john jane --last doe smith --company acme -o wordlist.txt
    
  Pattern generation:
    %(prog)s -p "admin%%%%"  "pass@@@@" -o wordlist.txt
    
  Everything combined:
    %(prog)s -w admin -u https://example.com --first john --last doe \\
             --company acme --dates --keyboard --leet --smart -o wordlist.txt

PATTERN SYNTAX:
  @  lowercase letter      ,  uppercase letter
  %%  digit                 ^  special character  
  ?  letter or digit       d  digit
  l  lowercase             u  uppercase
  s  special character
  
  Example: admin%%%% = admin + 4 digits
""")
    
    # Input sources
    input_group = parser.add_argument_group('INPUT')
    input_group.add_argument('-w', '--words', nargs='+', 
                            help='Base words for generation')
    input_group.add_argument('-i', '--input', dest='input_file',
                            help='File containing base words (one per line)')
    input_group.add_argument('-u', '--url', '--urls', dest='urls', nargs='+',
                            help='URLs to scrape for words')
    input_group.add_argument('-d', '--depth', type=int, default=1,
                            help='Web scraping depth (default: 1)')
    
    # Name-based generation
    name_group = parser.add_argument_group('NAMES')
    name_group.add_argument('--first', dest='first_names', nargs='+',
                           help='First names for combinations')
    name_group.add_argument('--last', dest='last_names', nargs='+',
                           help='Last names for combinations')
    name_group.add_argument('--company', help='Company name')
    
    # Generation options
    gen_group = parser.add_argument_group('GENERATION')
    gen_group.add_argument('-p', '--pattern', '--patterns', dest='patterns', nargs='+',
                          help='Pattern masks for generation')
    gen_group.add_argument('--dates', action='store_true',
                          help='Include date patterns (years, birthdays)')
    gen_group.add_argument('--keyboard', dest='keyboard_walks', action='store_true',
                          help='Include keyboard walk patterns')
    gen_group.add_argument('--leet', action='store_true',
                          help='Apply leetspeak transformations')
    gen_group.add_argument('--no-combo', dest='combinations', action='store_false',
                          help='Disable word combinations')
    gen_group.add_argument('--start-year', type=int, default=2015,
                          help='Start year for date generation (default: 2015)')
    gen_group.add_argument('--end-year', type=int,
                          help='End year for date generation')
    
    # Filters
    filter_group = parser.add_argument_group('FILTERS')
    filter_group.add_argument('--min', dest='min_length', type=int, default=1,
                            help='Minimum password length')
    filter_group.add_argument('--max', dest='max_length', type=int, default=128,
                            help='Maximum password length')
    filter_group.add_argument('--upper', dest='require_upper', action='store_true',
                            help='Require uppercase letters')
    filter_group.add_argument('--lower', dest='require_lower', action='store_true',
                            help='Require lowercase letters')
    filter_group.add_argument('--digit', dest='require_digit', action='store_true',
                            help='Require digits')
    filter_group.add_argument('--special', dest='require_special', action='store_true',
                            help='Require special characters')
    
    # Output
    output_group = parser.add_argument_group('OUTPUT')
    output_group.add_argument('-o', '--output', required=True,
                            help='Output file path')
    output_group.add_argument('--smart', dest='smart_order', action='store_true',
                            help='Sort by likelihood (slower but better)')
    output_group.add_argument('--stats', dest='save_stats', action='store_true',
                            help='Save generation statistics')
    output_group.add_argument('-v', '--verbose', action='store_true',
                            help='Verbose output')
    output_group.add_argument('--threads', type=int, default=4,
                            help='Threads for web scraping (default: 4)')
    
    args = parser.parse_args()
    
    # Build configuration
    config = vars(args)
    
    # Validate inputs
    has_input = any([
        config.get('words'),
        config.get('input_file'),
        config.get('urls'),
        config.get('patterns'),
        config.get('keyboard_walks'),
        (config.get('first_names') and config.get('last_names'))
    ])
    
    if not has_input:
        print("[!] Error: No input source specified")
        print("[!] Use -w for words, -u for URLs, -p for patterns, etc.")
        print("[!] Run with -h for help")
        sys.exit(1)
    
    # Run generation
    try:
        generator = PassGenPro(config)
        passwords = generator.generate()
        
        if passwords:
            generator.save(passwords, args.output)
            if args.verbose or args.save_stats:
                generator.print_stats()
        else:
            print("[!] No passwords generated")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
