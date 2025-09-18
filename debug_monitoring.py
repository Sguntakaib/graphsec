#!/usr/bin/env python3
"""
Debug script to understand why Monitoring vulnerability analysis is failing
"""

import sys
sys.path.append('/app/backend')

from vulnerability_rules import get_vulnerability_rules
from vulnerability_engine import VulnerabilityEngine

def debug_monitoring_rules():
    """Debug which monitoring rules exist and their trigger conditions"""
    
    print("🔍 DEBUGGING MONITORING VULNERABILITY RULES")
    print("=" * 60)
    
    # Get all rules
    all_rules = get_vulnerability_rules()
    
    # Filter for Monitoring rules
    monitoring_rules = [rule for rule in all_rules if "Monitoring" in rule.node_types]
    
    print(f"📊 Found {len(monitoring_rules)} Monitoring rules:")
    
    for i, rule in enumerate(monitoring_rules, 1):
        print(f"\n{i}. Rule ID: {rule.id}")
        print(f"   Name: {rule.name}")
        print(f"   Description: {rule.description}")
        print(f"   Trigger Conditions: {rule.trigger_conditions}")
        print(f"   Template Severity: {rule.vulnerability_template.get('severity', 'Unknown')}")
        print(f"   Template Category: {rule.vulnerability_template.get('category', 'Unknown')}")
    
    # Test with sample responses
    print("\n" + "=" * 60)
    print("🧪 TESTING WITH SAMPLE RESPONSES")
    print("=" * 60)
    
    # Sample responses from the browser logs
    sample_responses = {
        "monitoring_coverage": "basic",
        "alerting_enabled": False,
        "log_retention": "30_days", 
        "incident_response": False,
        "performance_monitoring": False
    }
    
    print(f"📋 Sample responses: {sample_responses}")
    
    # Check which rules would trigger
    engine = VulnerabilityEngine()
    
    for rule in monitoring_rules:
        would_trigger = engine._evaluate_rule(rule, sample_responses)
        print(f"\n🎯 Rule '{rule.id}' would trigger: {would_trigger}")
        
        if would_trigger:
            print(f"   ✅ TRIGGERED - Severity: {rule.vulnerability_template.get('severity')}")
            print(f"   ✅ TRIGGERED - Category: {rule.vulnerability_template.get('category')}")
            
            # Try to create the vulnerability node
            try:
                vuln_node = engine._create_vulnerability_node(
                    rule, "test-monitoring-node", "Monitoring", sample_responses, {"x": 0, "y": 0}, 0
                )
                print(f"   ✅ Vulnerability node created successfully")
                print(f"   📊 Severity: {vuln_node.severity}")
                print(f"   📊 Category: {vuln_node.category}")
            except Exception as e:
                print(f"   ❌ ERROR creating vulnerability node: {e}")
                print(f"   🔍 Error type: {type(e)}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    debug_monitoring_rules()