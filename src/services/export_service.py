import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from src.models.alumni import AlumniProfile, JobPosition


class ExportService:
    """Service for exporting alumni data to various formats"""
    
    def export_to_excel(self, 
                       alumni_profiles: List[AlumniProfile], 
                       filename: Optional[str] = None,
                       include_work_history: bool = True) -> str:
        """Export alumni profiles to Excel format"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alumni_export_{timestamp}.xlsx"
        
        # Ensure .xlsx extension
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        # Create main alumni data
        alumni_data = self.prepare_alumni_data(alumni_profiles)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main alumni sheet
            alumni_df = pd.DataFrame(alumni_data)
            alumni_df.to_excel(writer, sheet_name='Alumni', index=False)
            
            # Work history sheet (if requested)
            if include_work_history:
                work_history_data = self.prepare_work_history_data(alumni_profiles)
                if work_history_data:
                    work_history_df = pd.DataFrame(work_history_data)
                    work_history_df.to_excel(writer, sheet_name='Work History', index=False)
            
            # Summary statistics sheet
            summary_data = self.prepare_summary_data(alumni_profiles)
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        return filename
    
    def export_to_csv(self, 
                     alumni_profiles: List[AlumniProfile], 
                     filename: Optional[str] = None) -> str:
        """Export alumni profiles to CSV format"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alumni_export_{timestamp}.csv"
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        # Create alumni data
        alumni_data = self.prepare_alumni_data(alumni_profiles)
        alumni_df = pd.DataFrame(alumni_data)
        alumni_df.to_csv(filename, index=False)
        
        return filename
    
    def prepare_alumni_data(self, alumni_profiles: List[AlumniProfile]) -> List[Dict[str, Any]]:
        """Prepare alumni data for export"""
        data = []
        
        for profile in alumni_profiles:
            current_job = profile.get_current_job()
            
            row = {
                'ID': profile.id,
                'Full Name': profile.full_name,
                'Graduation Year': profile.graduation_year,
                'Current Job Title': current_job.title if current_job else '',
                'Current Company': current_job.company if current_job else '',
                'Current Industry': current_job.industry.value if current_job and current_job.industry else '',
                'Location': profile.location or '',
                'LinkedIn URL': profile.linkedin_url or '',
                'Industry': profile.industry.value if profile.industry else '',
                'Confidence Score': profile.confidence_score,
                'Last Updated': profile.last_updated.strftime('%Y-%m-%d %H:%M:%S') if profile.last_updated else '',
                'Total Jobs': len(profile.work_history),
                'Data Sources': ', '.join([source.source_type for source in profile.data_sources])
            }
            data.append(row)
        
        return data
    
    def prepare_work_history_data(self, alumni_profiles: List[AlumniProfile]) -> List[Dict[str, Any]]:
        """Prepare work history data for export"""
        data = []
        
        for profile in alumni_profiles:
            for job in profile.work_history:
                row = {
                    'Alumni ID': profile.id,
                    'Alumni Name': profile.full_name,
                    'Job Title': job.title,
                    'Company': job.company,
                    'Industry': job.industry.value if job.industry else '',
                    'Start Date': job.start_date.strftime('%Y-%m-%d') if job.start_date else '',
                    'End Date': job.end_date.strftime('%Y-%m-%d') if job.end_date else '',
                    'Is Current': 'Yes' if job.is_current else 'No',
                    'Location': job.location or '',
                    'Duration (Days)': self.calculate_job_duration(job)
                }
                data.append(row)
        
        return data
    
    def prepare_summary_data(self, alumni_profiles: List[AlumniProfile]) -> List[Dict[str, Any]]:
        """Prepare summary statistics for export"""
        if not alumni_profiles:
            return []
        
        # Industry distribution
        industry_counts = {}
        company_counts = {}
        graduation_year_counts = {}
        location_counts = {}
        
        for profile in alumni_profiles:
            # Count industries
            if profile.industry:
                industry_counts[profile.industry.value] = industry_counts.get(profile.industry.value, 0) + 1
            
            # Count companies (current job)
            current_job = profile.get_current_job()
            if current_job:
                company_counts[current_job.company] = company_counts.get(current_job.company, 0) + 1
            
            # Count graduation years
            if profile.graduation_year:
                graduation_year_counts[profile.graduation_year] = graduation_year_counts.get(profile.graduation_year, 0) + 1
            
            # Count locations
            if profile.location:
                location_counts[profile.location] = location_counts.get(profile.location, 0) + 1
        
        summary_data = []
        
        # Add general statistics
        summary_data.append({'Metric': 'Total Alumni', 'Value': len(alumni_profiles)})
        summary_data.append({'Metric': 'Alumni with Current Jobs', 'Value': sum(1 for p in alumni_profiles if p.get_current_job())})
        summary_data.append({'Metric': 'Alumni with LinkedIn', 'Value': sum(1 for p in alumni_profiles if p.linkedin_url)})
        summary_data.append({'Metric': 'Average Confidence Score', 'Value': f"{sum(p.confidence_score for p in alumni_profiles) / len(alumni_profiles):.2f}"})
        
        # Add empty row
        summary_data.append({'Metric': '', 'Value': ''})
        
        # Top industries
        summary_data.append({'Metric': 'TOP INDUSTRIES', 'Value': ''})
        for industry, count in sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            summary_data.append({'Metric': f'  {industry}', 'Value': count})
        
        # Add empty row
        summary_data.append({'Metric': '', 'Value': ''})
        
        # Top companies
        summary_data.append({'Metric': 'TOP COMPANIES', 'Value': ''})
        for company, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            summary_data.append({'Metric': f'  {company}', 'Value': count})
        
        return summary_data
    
    def calculate_job_duration(self, job: JobPosition) -> str:
        """Calculate job duration in days"""
        if not job.start_date:
            return ''
        
        end_date = job.end_date or datetime.now().date()
        duration = (end_date - job.start_date).days
        
        if duration < 30:
            return f"{duration} days"
        elif duration < 365:
            months = duration // 30
            return f"{months} months"
        else:
            years = duration // 365
            months = (duration % 365) // 30
            if months > 0:
                return f"{years} years, {months} months"
            else:
                return f"{years} years"
    
    def export_filtered_data(self, 
                           alumni_profiles: List[AlumniProfile],
                           filters: Dict[str, Any],
                           filename: Optional[str] = None) -> str:
        """Export filtered alumni data"""
        
        # Apply filters
        filtered_profiles = self.apply_filters(alumni_profiles, filters)
        
        # Generate filename with filter info
        if not filename:
            filter_str = "_".join([f"{k}-{v}" for k, v in filters.items() if v])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alumni_filtered_{filter_str}_{timestamp}.xlsx"
        
        return self.export_to_excel(filtered_profiles, filename)
    
    def apply_filters(self, 
                      alumni_profiles: List[AlumniProfile], 
                      filters: Dict[str, Any]) -> List[AlumniProfile]:
        """Apply filters to alumni profiles"""
        filtered = alumni_profiles
        
        if filters.get('industry'):
            filtered = [p for p in filtered if p.industry and p.industry.value == filters['industry']]
        
        if filters.get('graduation_year_min'):
            filtered = [p for p in filtered if p.graduation_year and p.graduation_year >= filters['graduation_year_min']]
        
        if filters.get('graduation_year_max'):
            filtered = [p for p in filtered if p.graduation_year and p.graduation_year <= filters['graduation_year_max']]
        
        if filters.get('location'):
            filtered = [p for p in filtered if p.location and filters['location'].lower() in p.location.lower()]
        
        if filters.get('company'):
            filtered = [p for p in filtered if p.get_current_job() and filters['company'].lower() in p.get_current_job().company.lower()]
        
        return filtered