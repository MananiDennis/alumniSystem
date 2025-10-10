#!/usr/bin/env python3
"""
Command Line Interface for Alumni Tracking System
"""
import argparse
import sys
from typing import List
from datetime import datetime
import time
from src.services.alumni_collector import AlumniCollector
from src.database.connection import db_manager


def collect_alumni_manual(names: List[str]):
    """Collect alumni data manually"""
    collector = AlumniCollector()
    
    try:
        print(f"Starting manual data collection for {len(names)} alumni...")
        profiles = collector.collect_alumni(names, method="manual")
        
        print(f"\n✓ Successfully collected data for {len(profiles)} alumni")
        
        # Display summary
        for profile in profiles:
            current_job = profile.get_current_job()
            job_info = f" - {current_job.title} at {current_job.company}" if current_job else ""
            print(f"  • {profile.full_name}{job_info}")
            
    except KeyboardInterrupt:
        print("\nData collection interrupted by user")
    except Exception as e:
        print(f"Error during data collection: {e}")
    finally:
        collector.close()


def search_alumni(name: str = None, industry: str = None, company: str = None, 
                 location: str = None, graduation_year: int = None, query: str = None):
    """Search for alumni in the database"""
    from src.services.search_service import SearchService
    
    search_service = SearchService()
    
    try:
        results = []
        
        if query:
            # Advanced text search
            results = search_service.search_alumni(name=query)
            print(f"Advanced search for: '{query}'")
        elif name:
            results = search_service.search_alumni(name=name)
            print(f"Searching by name: '{name}'")
        elif industry:
            results = search_service.search_alumni(industry=industry)
            print(f"Searching by industry: '{industry}'")
        elif company:
            results = search_service.search_alumni(company=company)
            print(f"🔍 Searching by company: '{company}'")
        elif location:
            results = search_service.search_alumni(location=location)
            print(f"🔍 Searching by location: '{location}'")
        elif graduation_year:
            results = search_service.search_alumni(graduation_year_min=graduation_year, graduation_year_max=graduation_year)
            print(f"🔍 Searching by graduation year: {graduation_year}")
        else:
            # Show recent alumni if no specific search
            results = search_service.repository.get_all_alumni(limit=20)
            print("📋 Recent alumni (last 20):")
        
        if not results:
            print("No alumni found matching the criteria")
            return
        
        print(f"✅ Found {len(results)} alumni:")
        for profile in results:
            current_job = profile.get_current_job()
            job_info = f" - {current_job.title} at {current_job.company}" if current_job else ""
            location_info = f" [{profile.location}]" if profile.location else ""
            confidence_info = f" (confidence: {profile.confidence_score:.2f})"
            print(f"  • {profile.full_name}{job_info}{location_info}{confidence_info}")
            
    except Exception as e:
        print(f"Error during search: {e}")
    finally:
        search_service.close()


def show_alumni_stats():
    """Show alumni database statistics"""
    from src.services.search_service import SearchService
    
    search_service = SearchService()
    
    try:
        stats = search_service.get_alumni_stats()
        
        print("Alumni Database Statistics")
        print("=" * 40)
        print(f"Total Alumni: {stats['total_count']}")
        print(f"With LinkedIn: {stats['with_linkedin']}")
        print(f"With Current Jobs: {stats['with_current_job']}")
        print(f"Average Confidence: {stats['average_confidence']:.2f}")
        
        print(f"\n🏢 Top Industries:")
        for industry, count in list(stats['industries'].items())[:5]:
            print(f"  • {industry}: {count}")
        
        print(f"\n📍 Top Locations:")
        for location, count in list(stats['locations'].items())[:5]:
            print(f"  • {location}: {count}")
        
        print(f"\n🏛️ Top Companies:")
        for company, count in list(stats['companies'].items())[:5]:
            if company != "Unknown":
                print(f"  • {company}: {count}")
        
        print(f"\n🎓 Graduation Years:")
        for year, count in list(stats['graduation_years'].items())[:10]:
            if year != "Unknown":
                print(f"  • {year}: {count}")
            
    except Exception as e:
        print(f"Error getting statistics: {e}")
    finally:
        search_service.close()


def list_all_alumni():
    """List all alumni in the database"""
    collector = AlumniCollector()
    
    try:
        all_alumni = collector.repository.get_all_alumni()
        
        if not all_alumni:
            print("No alumni found in database")
            return
        
        print(f"Total alumni in database: {len(all_alumni)}")
        for profile in all_alumni:
            current_job = profile.get_current_job()
            job_info = f" - {current_job.title} at {current_job.company}" if current_job else ""
            grad_year = f" (Class of {profile.graduation_year})" if profile.graduation_year else ""
            print(f"  • {profile.full_name}{grad_year}{job_info}")
            
    except Exception as e:
        print(f"Error listing alumni: {e}")
    finally:
        collector.close()


def export_alumni(format_type: str = 'excel', filters: dict = None):
    """Export alumni data to Excel or CSV"""
    from src.services.export_service import ExportService
    
    collector = AlumniCollector()
    export_service = ExportService()
    
    try:
        # Get all alumni
        all_alumni = collector.repository.get_all_alumni()
        
        if not all_alumni:
            print("No alumni found in database to export")
            return
        
        # Export based on format
        if format_type.lower() == 'csv':
            filename = export_service.export_to_csv(all_alumni)
            print(f"✓ Exported {len(all_alumni)} alumni to {filename}")
        elif filters:
            filename = export_service.export_filtered_data(all_alumni, filters)
            print(f"✓ Exported filtered alumni data to {filename}")
        else:
            filename = export_service.export_to_excel(all_alumni)
            print(f"✓ Exported {len(all_alumni)} alumni to {filename}")
        
        print(f"File saved: {filename}")
            
    except Exception as e:
        print(f"Error exporting alumni: {e}")
    finally:
        collector.close()


def collect_alumni_linkedin(names: List[str], graduation_years: List[int] = None):
    """Collect alumni data using BrightData LinkedIn scraping"""
    collector = AlumniCollector()
    
    try:
        print(f"🚀 Starting BrightData collection for {len(names)} alumni...")
        print("Using professional LinkedIn data API - high accuracy guaranteed!")
        
        profiles = collector.collect_alumni(names, method="brightdata")
        
        print(f"\n✅ Successfully processed {len(profiles)} alumni profiles")
        
        # Display results
        for profile in profiles:
            current_job = profile.get_current_job()
            job_info = f" - {current_job.title} at {current_job.company}" if current_job else ""
            confidence_info = f" (confidence: {profile.confidence_score:.2f})"
            location_info = f" [{profile.location}]" if profile.location else ""
            print(f"  • {profile.full_name}{job_info}{location_info}{confidence_info}")
        
        # Show statistics
        stats = collector.get_stats()
        print(f"\n📊 Collection Statistics:")
        print(f"  Total alumni in database: {stats['total_alumni']}")
        print(f"  With LinkedIn profiles: {stats['with_linkedin']}")
        print(f"  With current jobs: {stats['with_current_job']}")
        print(f"  Average confidence: {stats['average_confidence']:.2f}")
        
        if stats['by_industry']:
            print(f"  Industries: {', '.join(stats['by_industry'].keys())}")
            
    except ValueError as e:
        if "BrightData API key" in str(e):
            print("BrightData API credentials not configured!")
            print("Please add BRIGHTDATA_API_KEY and BRIGHTDATA_DATASET_ID to your .env file")
        else:
            print(f"Configuration error: {e}")
    except KeyboardInterrupt:
        print("\nData collection interrupted by user")
    except Exception as e:
        print(f"Error during BrightData collection: {e}")
        import traceback
        traceback.print_exc()
    finally:
        collector.close()


def collect_alumni_web_research(names: List[str]):
    """Collect alumni data using web research + AI"""
    collector = AlumniCollector()
    
    try:
        print(f"🌐 Starting web research collection for {len(names)} alumni...")
        print("Using web scraping + AI for data extraction and structuring")
        
        profiles = collector.collect_alumni(names, method="web-research")
        
        print(f"\n✅ Successfully processed {len(profiles)} alumni profiles")
        
        # Display results
        for profile in profiles:
            current_job = profile.get_current_job()
            job_info = f" - {current_job.title} at {current_job.company}" if current_job else ""
            confidence_info = f" (confidence: {profile.confidence_score:.2f})"
            location_info = f" [{profile.location}]" if profile.location else ""
            print(f"  • {profile.full_name}{job_info}{location_info}{confidence_info}")
        
        # Show statistics
        stats = collector.get_stats()
        print(f"\n📊 Collection Statistics:")
        print(f"  Total alumni in database: {stats['total_alumni']}")
        print(f"  With LinkedIn profiles: {stats['with_linkedin']}")
        print(f"  With current jobs: {stats['with_current_job']}")
        print(f"  Average confidence: {stats['average_confidence']:.2f}")
        
        if stats['by_industry']:
            print(f"  Industries: {', '.join(stats['by_industry'].keys())}")
            
    except ValueError as e:
        if "AI service" in str(e):
            print("AI service not available!")
            print("Please add OPENAI_API_KEY to your .env file for web research")
        else:
            print(f"Configuration error: {e}")
    except KeyboardInterrupt:
        print("\nData collection interrupted by user")
    except Exception as e:
        print(f"Error during web research collection: {e}")
        import traceback
        traceback.print_exc()
    finally:
        collector.close()


def update_alumni_profiles(profile_ids: List[int] = None, max_age_days: int = 30):
    """Update existing alumni profiles with fresh data"""
    from src.services.update_service import UpdateService
    
    update_service = UpdateService()
    
    try:
        if profile_ids:
            print(f"🔄 Updating specific profiles: {profile_ids}")
            updated_profiles = update_service.batch_update_by_ids(profile_ids)
        else:
            print(f"🔄 Updating all profiles older than {max_age_days} days...")
            updated_profiles = update_service.update_all_profiles(max_age_days)
        
        print(f"✅ Updated {len(updated_profiles)} profiles")
        for profile in updated_profiles:
            current_job = profile.get_current_job()
            job_info = f" - {current_job.title} at {current_job.company}" if current_job else ""
            print(f"  • {profile.full_name}{job_info} (updated: {profile.last_updated.strftime('%Y-%m-%d %H:%M')})")
            
    except Exception as e:
        print(f"Error updating profiles: {e}")
    finally:
        update_service.close()


def show_update_stats():
    """Show update statistics"""
    from src.services.update_service import UpdateService
    
    update_service = UpdateService()
    
    try:
        stats = update_service.get_update_stats()
        
        print("Profile Update Statistics")
        print("=" * 40)
        print(f"Total Profiles: {stats['total_profiles']}")
        print(f"With LinkedIn URLs: {stats['with_linkedin']}")
        print(f"Updated Today: {stats['updated_today']}")
        print(f"Updated This Week: {stats['updated_this_week']}")
        print(f"Updated This Month: {stats['updated_this_month']}")
        print(f"Need Update (30+ days): {stats['needs_update_30_days']}")
        print(f"Need Update (90+ days): {stats['needs_update_90_days']}")
        
        # Show candidates for update
        candidates = update_service.get_update_candidates()
        if candidates:
            print(f"\n🔄 Update Candidates ({len(candidates)}):")
            for alumni in candidates[:10]:  # Show first 10
                days_old = (datetime.now() - alumni.last_updated).days
                print(f"  • {alumni.full_name} (last updated {days_old} days ago)")
            if len(candidates) > 10:
                print(f"  ... and {len(candidates) - 10} more")
        else:
            print(f"\n✅ All profiles are up to date!")
            
    except Exception as e:
        print(f"Error getting update stats: {e}")
    finally:
        update_service.close()


def web_research_alumni(names: List[str], additional_info: str = None):
    """Search for alumni using web research"""
    from src.services.web_research_service import WebResearchService
    
    research_service = WebResearchService()
    
    try:
        print(f"🌐Starting web research for {len(names)} alumni...")
        if additional_info:
            print(f"Additional context: {additional_info}")
        
        # Research each person
        for name in names:
            print(f"\nResearching: {name}")
            results = research_service.search_person_web(name, additional_info or "")
            
            if not results:
                print("  No results found")
                continue
            
            print(f"Found {len(results)} potential matches:")
            for i, result in enumerate(results[:5], 1):  # Show top 5
                title = result.get('title', 'No title')[:80]
                url = result.get('url', 'No URL')
                snippet = result.get('snippet', '')[:100]
                print(f"    {i}. {title}")
                print(f"       {url}")
                if snippet:
                    print(f"       \"{snippet}...\"")
                print()
                
            # Extract professional info from top result if available
            if results and results[0].get('url'):
                print("  📋 Analyzing top result...")
                try:
                    info = research_service.extract_professional_info(results[0]['url'])
                    if info.get('has_linkedin'):
                        print("    ✅ LinkedIn profile detected")
                    if info.get('has_professional_info'):
                        print("    ✅ Professional information found")
                    if info.get('mentions_ecu'):
                        print("    ✅ ECU connection mentioned")
                except Exception as e:
                    print(f"    Error analyzing page: {e}")
            
            time.sleep(1)  # Be respectful
            
    except Exception as e:
        print(f"Error during web research: {e}")
    finally:
        pass  # No close method needed


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Alumni Tracking System CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Collect command (manual)
    collect_parser = subparsers.add_parser('collect', help='Collect alumni data manually')
    collect_parser.add_argument('names', nargs='+', help='Names of alumni to collect data for')
    
    # LinkedIn collect command
    linkedin_parser = subparsers.add_parser('linkedin', help='Collect alumni data using LinkedIn scraping')
    linkedin_parser.add_argument('names', nargs='+', help='Names of alumni to collect data for')
    linkedin_parser.add_argument('--graduation-years', nargs='+', type=int, help='Graduation years (optional)')
    
    # Web research collect command
    web_parser = subparsers.add_parser('web-research', help='Collect alumni data using web research')
    web_parser.add_argument('names', nargs='+', help='Names of alumni to collect data for')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update existing profiles with fresh data')
    update_parser.add_argument('--ids', nargs='+', type=int, help='Specific profile IDs to update (optional)')
    update_parser.add_argument('--max-age-days', type=int, default=30, help='Update profiles older than N days (default: 30)')
    
    # Update stats command
    update_stats_parser = subparsers.add_parser('update-stats', help='Show profile update statistics')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for alumni')
    search_parser.add_argument('--name', help='Search by name')
    search_parser.add_argument('--industry', help='Search by industry')
    search_parser.add_argument('--company', help='Search by company')
    search_parser.add_argument('--location', help='Search by location')
    search_parser.add_argument('--graduation-year', type=int, help='Search by graduation year')
    search_parser.add_argument('--query', help='Advanced text search across all fields')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all alumni')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export alumni data')
    export_parser.add_argument('--format', choices=['excel', 'csv'], default='excel', help='Export format')
    export_parser.add_argument('--industry', help='Filter by industry')
    export_parser.add_argument('--graduation-year-min', type=int, help='Minimum graduation year')
    export_parser.add_argument('--graduation-year-max', type=int, help='Maximum graduation year')
    export_parser.add_argument('--location', help='Filter by location')
    export_parser.add_argument('--company', help='Filter by company')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show alumni database statistics')
    
    # Web research command
    web_research_parser = subparsers.add_parser('web-research', help='Search for alumni using web research')
    web_research_parser.add_argument('names', nargs='+', help='Names of alumni to research')
    web_research_parser.add_argument('--additional-info', help='Additional search context (e.g., graduation year, location)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize database
    print("Initializing database...")
    db_manager.create_tables()
    
    if args.command == 'collect':
        collect_alumni_manual(args.names)
    elif args.command == 'linkedin':
        collect_alumni_linkedin(args.names, args.graduation_years)
    elif args.command == 'web-research':
        collect_alumni_web_research(args.names)
    elif args.command == 'update':
        update_alumni_profiles(args.ids, getattr(args, 'max_age_days', 30))
    elif args.command == 'update-stats':
        show_update_stats()
    elif args.command == 'search':
        search_alumni(args.name, args.industry, args.company, args.location, 
                     getattr(args, 'graduation_year', None), args.query)
    elif args.command == 'stats':
        show_alumni_stats()
    elif args.command == 'list':
        list_all_alumni()
    elif args.command == 'export':
        filters = {}
        if args.industry:
            filters['industry'] = args.industry
        if args.graduation_year_min:
            filters['graduation_year_min'] = args.graduation_year_min
        if args.graduation_year_max:
            filters['graduation_year_max'] = args.graduation_year_max
        if args.location:
            filters['location'] = args.location
        if args.company:
            filters['company'] = args.company
        
        export_alumni(args.format, filters if filters else None)
    elif args.command == 'stats':
        show_alumni_stats()
    elif args.command == 'web-research':
        web_research_alumni(args.names, getattr(args, 'additional_info', None))


def show_alumni_stats():
    """Show comprehensive alumni statistics"""
    from src.services.search_service import SearchService
    from src.services.update_service import UpdateService
    
    search_service = SearchService()
    update_service = UpdateService()
    
    try:
        print("📊 Alumni Database Statistics\n")
        
        # Get comprehensive stats
        stats = search_service.get_alumni_stats()
        update_stats = update_service.get_update_statistics()
        
        # Basic stats
        print(f"👥 Total Alumni: {stats['total_alumni']}")
        print(f"🔗 With LinkedIn: {stats['with_linkedin']}")
        print(f"💼 With Current Job: {stats['with_current_job']}")
        print(f"📍 With Location: {stats['with_location']}")
        print(f"📊 Average Confidence: {stats['average_confidence']:.2f}")
        
        # Industry distribution
        print(f"\n🏢 Top Industries:")
        for industry, count in list(stats['industry_distribution'].items())[:5]:
            print(f"  • {industry}: {count}")
        
        # Top companies
        print(f"\n🏆 Top Companies:")
        for company_info in stats['top_companies']:
            print(f"  • {company_info['company']}: {company_info['alumni_count']} alumni")
        
        # Location distribution
        print(f"\n🌍 Top Locations:")
        for location, count in list(stats['location_distribution'].items())[:5]:
            print(f"  • {location}: {count}")
        
        # Update freshness
        print(f"\n🔄 Data Freshness:")
        print(f"  • Fresh (< 7 days): {update_stats['fresh_profiles']}")
        print(f"  • Recent (7-30 days): {update_stats['recent_profiles']}")
        print(f"  • Old (30-90 days): {update_stats['old_profiles']}")
        print(f"  • Very old (> 90 days): {update_stats['very_old_profiles']}")
        print(f"  • Average age: {update_stats['average_age_days']:.1f} days")
        
        # Suggestions
        if update_stats['very_old_profiles'] > 0:
            print(f"\n💡 Suggestion: Update {update_stats['very_old_profiles']} very old profiles")
            print("   Run: python -m src.cli update")
        
    except Exception as e:
        print(f"Error getting statistics: {e}")
    finally:
        search_service.close()
        update_service.close()


if __name__ == '__main__':
    main()