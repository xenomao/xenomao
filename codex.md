# DigiLab Beauty AI Organization System

## Project Overview
This is the DigiLab Beauty AI organization system, managing 18 esthetic industry companies for B2B sales outreach.

## AI Agents
- @AI Executive Officer - Strategy & KPI management
- @AI Sales - Sales outreach to 18 companies (Tier A/B/C)
- @AI Marketing - PR, SNS, content creation via Lovart AI
- @AI Intelligence - News collection via NewsAPI, industry monitoring
- @AI Secretary - Email procedures, document management

## Key Files
- `scripts/main.py` - Main setup script (DB init, company import, news collection)
- `scripts/daily_news_collection.py` - Daily news collection from NewsAPI
- `db/digilab_beauty.db` - SQLite database with 8 tables
- `db/esthetic_industry_dd_19companies.csv` - Source data for 18 companies
- `marketing/digilab_beauty_flyer.html` - A4 printable flyer

## Database Schema
8 tables: companies, contacts, contact_history, tasks, sales_pipeline, documents, intelligence_log, kpi_tracking

## Tech Stack
- Python 3.12 for scripts
- SQLite for database
- NewsAPI for news collection
- Lovart AI for design generation

## Conventions
- All documentation in Japanese
- Brand colors: Purple (#8b2fc9), Pink (#d946a8), Gold (#ffd700)
- File naming: snake_case
