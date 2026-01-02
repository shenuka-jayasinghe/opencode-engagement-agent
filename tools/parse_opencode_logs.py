#!/usr/bin/env python3
"""
OpenCode Log Parser for Usage Tracking
Parses OpenCode logs to extract API usage and populate usage_tracker.db
"""

import re
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse

class OpenCodeLogParser:
    def __init__(self, log_dir: str = None):
        if log_dir is None:
            self.log_dir = Path.home() / ".local/share/opencode/log"
        else:
            self.log_dir = Path(log_dir)
        
        # Map OpenCode provider IDs to our tracker format
        self.provider_map = {
            "google": "google",
            "anthropic": "anthropic",
            "amazon-bedrock": "amazon-bedrock",
            "github-copilot": "github-copilot",
        }
    
    def parse_log_line(self, line: str) -> Optional[Dict]:
        """Parse a single log line for API call information"""
        # Example log format:
        # ERROR 2025-12-31T14:43:46 +86ms service=llm providerID=google modelID=gemini-3-flash-preview sessionID=ses_...
        
        # Extract timestamp
        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
        if not timestamp_match:
            return None
        
        timestamp = timestamp_match.group(1)
        
        # Extract provider
        provider_match = re.search(r'providerID=([^\s]+)', line)
        if not provider_match:
            return None
        provider_id = provider_match.group(1)
        
        # Extract model
        model_match = re.search(r'modelID=([^\s]+)', line)
        if not model_match:
            return None
        model_id = model_match.group(1)
        
        # Extract session
        session_match = re.search(r'sessionID=([^\s]+)', line)
        session_id = session_match.group(1) if session_match else None
        
        # Try to extract token usage if present
        # This is speculative - actual format may vary
        input_tokens = None
        output_tokens = None
        
        token_match = re.search(r'"inputTokens":(\d+).*"outputTokens":(\d+)', line)
        if token_match:
            input_tokens = int(token_match.group(1))
            output_tokens = int(token_match.group(2))
        
        return {
            "timestamp": timestamp,
            "provider": self.provider_map.get(provider_id, provider_id),
            "model": f"{self.provider_map.get(provider_id, provider_id)}/{model_id}",
            "session_id": session_id,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "raw_line": line[:200]  # Keep snippet for debugging
        }
    
    def parse_log_file(self, log_file: Path) -> List[Dict]:
        """Parse a single log file"""
        api_calls = []
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if 'providerID=' in line and 'modelID=' in line:
                        parsed = self.parse_log_line(line)
                        if parsed:
                            api_calls.append(parsed)
        except Exception as e:
            print(f"Error parsing {log_file}: {e}")
        
        return api_calls
    
    def parse_all_logs(self) -> List[Dict]:
        """Parse all log files in the directory"""
        all_calls = []
        
        log_files = sorted(self.log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        for log_file in log_files:
            print(f"Parsing {log_file.name}...")
            calls = self.parse_log_file(log_file)
            all_calls.extend(calls)
            print(f"  Found {len(calls)} API calls")
        
        return all_calls
    
    def get_recent_logs(self, days: int = 7) -> List[Dict]:
        """Parse only recent log files"""
        all_calls = []
        cutoff = datetime.now().timestamp() - (days * 86400)
        
        log_files = sorted(self.log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        for log_file in log_files:
            if log_file.stat().st_mtime < cutoff:
                break
            
            print(f"Parsing {log_file.name}...")
            calls = self.parse_log_file(log_file)
            all_calls.extend(calls)
            print(f"  Found {len(calls)} API calls")
        
        return all_calls
    
    def import_to_tracker(self, tracker_db: str, api_calls: List[Dict], session_id: int):
        """Import parsed API calls into usage tracker database"""
        conn = sqlite3.connect(tracker_db)
        cursor = conn.cursor()
        
        imported = 0
        skipped = 0
        
        for call in api_calls:
            # Skip if no token data
            if call['input_tokens'] is None or call['output_tokens'] is None:
                skipped += 1
                continue
            
            try:
                cursor.execute("""
                    INSERT INTO api_calls 
                    (session_id, timestamp, provider, model, operation, input_tokens, output_tokens, total_tokens, cost)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    call['timestamp'],
                    call['provider'],
                    call['model'],
                    'parsed-from-log',
                    call['input_tokens'],
                    call['output_tokens'],
                    call['input_tokens'] + call['output_tokens'],
                    0.0  # Cost will be calculated by trigger or manually
                ))
                imported += 1
            except Exception as e:
                print(f"Error importing call: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Imported {imported} API calls")
        print(f"⏭️  Skipped {skipped} calls (no token data)")
    
    def generate_summary(self, api_calls: List[Dict]) -> Dict:
        """Generate summary statistics from API calls"""
        total_calls = len(api_calls)
        calls_with_tokens = [c for c in api_calls if c['input_tokens'] is not None]
        
        total_input = sum(c['input_tokens'] for c in calls_with_tokens)
        total_output = sum(c['output_tokens'] for c in calls_with_tokens)
        
        # Group by model
        by_model = {}
        for call in api_calls:
            model = call['model']
            if model not in by_model:
                by_model[model] = {'count': 0, 'input': 0, 'output': 0}
            by_model[model]['count'] += 1
            if call['input_tokens']:
                by_model[model]['input'] += call['input_tokens']
            if call['output_tokens']:
                by_model[model]['output'] += call['output_tokens']
        
        return {
            'total_calls': total_calls,
            'calls_with_token_data': len(calls_with_tokens),
            'total_input_tokens': total_input,
            'total_output_tokens': total_output,
            'total_tokens': total_input + total_output,
            'by_model': by_model
        }


def main():
    parser = argparse.ArgumentParser(description="Parse OpenCode logs for usage tracking")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Parse logs
    parse_parser = subparsers.add_parser("parse", help="Parse log files")
    parse_parser.add_argument("--days", type=int, default=7, help="Days to look back")
    parse_parser.add_argument("--all", action="store_true", help="Parse all logs")
    
    # Import to tracker
    import_parser = subparsers.add_parser("import", help="Import to usage tracker")
    import_parser.add_argument("session_id", type=int, help="Session ID to import into")
    import_parser.add_argument("--days", type=int, default=7, help="Days to look back")
    
    # Summary
    summary_parser = subparsers.add_parser("summary", help="Show summary of logs")
    summary_parser.add_argument("--days", type=int, default=7, help="Days to look back")
    
    args = parser.parse_args()
    
    log_parser = OpenCodeLogParser()
    
    if args.command == "parse":
        if args.all:
            api_calls = log_parser.parse_all_logs()
        else:
            api_calls = log_parser.get_recent_logs(args.days)
        
        print(f"\n📊 Found {len(api_calls)} total API calls")
        
        summary = log_parser.generate_summary(api_calls)
        print(f"📝 {summary['calls_with_token_data']} calls have token data")
        print(f"🎯 Total tokens: {summary['total_tokens']:,}")
        
        # Save to JSON for inspection
        output_file = Path("parsed_api_calls.json")
        with open(output_file, 'w') as f:
            json.dump(api_calls, f, indent=2)
        print(f"\n💾 Saved to {output_file}")
    
    elif args.command == "import":
        api_calls = log_parser.get_recent_logs(args.days)
        tracker_db = Path(__file__).parent.parent / "usage_tracker.db"
        
        print(f"📊 Importing {len(api_calls)} API calls to session {args.session_id}...")
        log_parser.import_to_tracker(str(tracker_db), api_calls, args.session_id)
    
    elif args.command == "summary":
        api_calls = log_parser.get_recent_logs(args.days)
        summary = log_parser.generate_summary(api_calls)
        
        print(f"\n=== OpenCode Usage Summary (Last {args.days} Days) ===\n")
        print(f"Total API Calls: {summary['total_calls']}")
        print(f"Calls with Token Data: {summary['calls_with_token_data']}")
        print(f"Total Input Tokens: {summary['total_input_tokens']:,}")
        print(f"Total Output Tokens: {summary['total_output_tokens']:,}")
        print(f"Total Tokens: {summary['total_tokens']:,}")
        
        print("\n=== By Model ===")
        for model, stats in summary['by_model'].items():
            print(f"\n{model}")
            print(f"  Calls: {stats['count']}")
            print(f"  Input Tokens: {stats['input']:,}")
            print(f"  Output Tokens: {stats['output']:,}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
