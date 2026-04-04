#!/usr/bin/env python3
"""
Interactive Google Ads Report Generator
For use when API access is not available
"""

import sys

def get_input(prompt, default=""):
    """Get user input with optional default"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()

def get_float_input(prompt, default=0.0):
    """Get float input"""
    while True:
        try:
            val = get_input(prompt, str(default))
            return float(val) if val else default
        except ValueError:
            print("Please enter a valid number")

def get_int_input(prompt, default=0):
    """Get integer input"""
    while True:
        try:
            val = get_input(prompt, str(default))
            return int(float(val)) if val else default
        except ValueError:
            print("Please enter a valid number")

def collect_campaign_data():
    """Collect campaign data from user"""
    campaigns = []
    
    print("\nEnter campaign data (leave name empty to finish):")
    print("-" * 50)
    
    while True:
        print(f"\nCampaign #{len(campaigns) + 1}")
        name = get_input("Campaign name")
        
        if not name:
            break
        
        spend = get_float_input("  Total spend ($)", 0)
        leads = get_int_input("  Leads/conversions", 0)
        clicks = get_int_input("  Clicks", 0)
        impressions = get_int_input("  Impressions", 0)
        
        cpl = spend / leads if leads > 0 else 0
        
        campaigns.append({
            'name': name,
            'spend': spend,
            'leads': leads,
            'clicks': clicks,
            'impressions': impressions,
            'cpl': cpl
        })
        
        print(f"  → CPL: ${cpl:.2f}")
    
    return campaigns

def generate_report_interactive():
    """Interactive report generation"""
    
    print("=" * 60)
    print("GOOGLE ADS WEEKLY REPORT GENERATOR")
    print("=" * 60)
    print()
    
    # Select client
    print("Select client:")
    print("1. Dental Artistry (Riya)")
    print("2. Lumiere Dental (Dr. Allababidi)")
    
    choice = get_input("Enter 1 or 2", "1")
    
    if choice == "1":
        client_name = "Dental Artistry"
        recipient = "Riya"
        client_type = "dental_artistry"
    else:
        client_name = "Lumiere Dental"
        recipient = "Dr. Allababidi"
        client_type = "lumiere"
    
    # Get date range
    print(f"\n{client_name} - {recipient}")
    print("-" * 40)
    
    start_date = get_input("Start date (e.g., Feb 18)", "Feb 18")
    end_date = get_input("End date (e.g., Feb 24)", "Feb 24")
    year = get_input("Year", "2026")
    
    # Collect campaign data
    campaigns = collect_campaign_data()
    
    if not campaigns:
        print("No campaigns entered. Exiting.")
        return
    
    # Calculate totals
    total_spend = sum(c['spend'] for c in campaigns)
    total_leads = sum(c['leads'] for c in campaigns)
    avg_cpl = total_spend / total_leads if total_leads > 0 else 0
    
    # Show summary
    print("\n" + "=" * 60)
    print("DATA SUMMARY")
    print("=" * 60)
    print(f"Total Spend: ${total_spend:,.2f}")
    print(f"Total Leads: {total_leads}")
    print(f"Average CPL: ${avg_cpl:.2f}")
    print(f"Campaigns: {len(campaigns)}")
    
    # Generate report
    print("\nGenerating report...")
    
    # Import formatter
    sys.path.insert(0, '/data/workspace/scripts')
    from format_report import generate_dental_artistry_report, generate_lumiere_report
    
    data = {
        'campaigns': campaigns,
        'search_terms': []  # Could add search term input later
    }
    
    date_range = f"{start_date}-{end_date}, {year}"
    
    if client_type == "dental_artistry":
        report = generate_dental_artistry_report(data, start_date, end_date)
    else:
        report = generate_lumiere_report(data, start_date, end_date)
    
    # Save report
    filename = f"/data/workspace/reports/{client_name.lower().replace(' ', '_')}_{start_date}_{end_date}.txt"
    with open(filename, 'w') as f:
        f.write(report)
    
    print(f"\n✓ Report saved to: {filename}")
    
    # Display report
    print("\n" + "=" * 60)
    print("REPORT PREVIEW")
    print("=" * 60)
    print(report)
    
    print("\n" + "=" * 60)
    print("To send to Slack, copy the report above and paste it")
    print("Or use: openclaw agent --agent clover --message \"Send this report to Slack...\"")
    print("=" * 60)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        # Quick mode with sample data for testing
        print("Quick test mode...")
        sys.path.insert(0, '/data/workspace/scripts')
        from format_report import generate_dental_artistry_report
        
        sample_data = {
            'campaigns': [
                {'name': 'PMAX Branded', 'spend': 374, 'leads': 17, 'clicks': 120, 'impressions': 4500, 'cpl': 22},
                {'name': 'PMAX Competitors', 'spend': 136, 'leads': 8, 'clicks': 89, 'impressions': 3200, 'cpl': 17},
                {'name': 'Implants', 'spend': 630, 'leads': 10, 'clicks': 234, 'impressions': 8900, 'cpl': 63},
            ]
        }
        
        report = generate_dental_artistry_report(sample_data, "Feb 18-24", "2026")
        print(report)
        return
    
    # Interactive mode
    try:
        generate_report_interactive()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)

if __name__ == '__main__':
    main()
