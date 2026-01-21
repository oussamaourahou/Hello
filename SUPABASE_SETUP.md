# Supabase Setup Guide for Palete Studio

This guide will help you set up Supabase for the Palete Studio application.

## Step 1: Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `palete-studio` (or your preference)
   - **Database Password**: Save this securely!
   - **Region**: Choose closest to your users (e.g., `eu-central-1` for Europe)
   - **Pricing Plan**: Start with **Free tier** (500MB database, 1GB storage, 50,000 monthly active users)

## Step 2: Run the Database Migration

1. Once your project is created, go to the **SQL Editor** in the Supabase dashboard
2. Click "New Query"
3. Copy the contents of `backend/database/migrations/001_initial_schema.sql`
4. Paste into the SQL Editor
5. Click "Run" to execute the migration
6. You should see: "Success. No rows returned"

This creates:
- ✅ 3 tables: `restaurants`, `menu_items`, `photos`
- ✅ Foreign key relationships
- ✅ Row Level Security (RLS) policies
- ✅ Indexes for performance
- ✅ Auto-update triggers for `updated_at`

## Step 3: Create Storage Bucket

1. Go to **Storage** in the Supabase dashboard
2. Click "Create a new bucket"
3. Enter bucket details:
   - **Name**: `palete-photos`
   - **Public bucket**: ✅ Check this (images need to be publicly accessible)
4. Click "Create bucket"

### Configure Storage Policies

1. Click on the `palete-photos` bucket
2. Go to **Policies** tab
3. Create the following policies:

**Policy 1: Allow authenticated users to upload**
```sql
CREATE POLICY "Authenticated users can upload photos"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'palete-photos');
```

**Policy 2: Allow public read access**
```sql
CREATE POLICY "Public can view photos"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'palete-photos');
```

**Policy 3: Allow users to delete own photos**
```sql
CREATE POLICY "Users can delete own photos"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'palete-photos');
```

## Step 4: Get API Credentials

1. Go to **Settings** → **API** in the Supabase dashboard
2. Copy the following values:

   - **Project URL**: `https://xxxxx.supabase.co`
   - **Service Role Key** (⚠️ Keep this secret!): `eyJhbGc...`

3. Update your `.env` file:

```env
# Supabase Database & Storage
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...your_service_role_key_here
```

⚠️ **IMPORTANT**: Use the **Service Role Key** (not the anon key) for backend operations. This key bypasses Row Level Security and should never be exposed to the client.

## Step 5: Verify Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Test the database connection:
```python
from backend.services.database_service import get_database_service

db = get_database_service()
print("✅ Database connected successfully!")
```

## Database Schema Overview

### Table: `restaurants`
Stores restaurant information and workflow status.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `owner_user_id` | TEXT | Clerk user ID |
| `name` | TEXT | Restaurant name |
| `cuisine_type` | TEXT | Type of cuisine (optional) |
| `status` | TEXT | `draft`, `processing`, `ready`, `exported` |
| `created_at` | TIMESTAMP | Auto-generated |
| `updated_at` | TIMESTAMP | Auto-updated |

### Table: `photos`
Stores uploaded and AI-generated food photos.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `restaurant_id` | UUID | Foreign key to `restaurants` |
| `filename` | TEXT | Original filename |
| `storage_path` | TEXT | Supabase Storage URL |
| `thumbnail_url` | TEXT | Thumbnail URL (optional) |
| `source` | TEXT | `uploaded` or `generated` |
| `generation_model` | TEXT | `dall-e-3` if generated |
| `uploaded_at` | TIMESTAMP | Auto-generated |

### Table: `menu_items`
Stores menu items with AI matching and enhancement data.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `restaurant_id` | UUID | Foreign key to `restaurants` |
| `name` | TEXT | Menu item name |
| `description` | TEXT | Description (optional) |
| `price` | DECIMAL | Price (optional) |
| `category` | TEXT | Category (optional) |
| `matched_photo_id` | UUID | Foreign key to `photos` |
| `match_confidence` | INTEGER | 0-100 confidence score |
| `match_reasoning` | TEXT | AI matching explanation |
| `photo_source` | TEXT | `uploaded`, `generated`, or `none` |
| `enhanced_photo_url` | TEXT | Photoroom enhanced URL |
| `quality_score` | INTEGER | 0-100 quality score |
| `quality_details` | JSONB | Full quality assessment JSON |
| `needs_review` | BOOLEAN | Flags for manual review |
| `created_at` | TIMESTAMP | Auto-generated |
| `updated_at` | TIMESTAMP | Auto-updated |

## Pricing Considerations

### Free Tier Limits
- ✅ 500 MB database space
- ✅ 1 GB storage space
- ✅ 50,000 monthly active users
- ✅ 500 MB bandwidth per month

### When to Upgrade to Pro ($25/month)
- 8 GB database space
- 100 GB storage space
- Unlimited monthly active users
- 250 GB bandwidth per month
- Daily backups
- Point-in-time recovery

For a typical Glovo restaurant use case:
- **10 restaurants** × **50 menu items** × **2 photos each** (original + enhanced)
- Avg photo size: 300 KB
- Total storage: ~30 MB (well within free tier!)

**Recommendation**: Start with free tier and upgrade when you have 50+ restaurants or 5GB+ of photos.

## Troubleshooting

### Error: "relation does not exist"
- ✅ Make sure you ran the migration SQL in Step 2
- ✅ Check that all tables were created: `restaurants`, `photos`, `menu_items`

### Error: "permission denied for table"
- ✅ Make sure you're using the **Service Role Key** (not anon key)
- ✅ Check that RLS policies are enabled

### Error: "No bucket found"
- ✅ Create the `palete-photos` bucket in Storage
- ✅ Make sure it's set to **public**

### Images not loading
- ✅ Check storage policies allow public SELECT
- ✅ Verify bucket is public
- ✅ Check CORS settings if accessing from different domain

## Next Steps

Once Supabase is set up:
1. ✅ Test the restaurant creation endpoint: `POST /api/restaurants`
2. ✅ Upload menu and photos: `POST /api/restaurants/{id}/upload-menu`
3. ✅ Run the full 5-screen workflow
4. ✅ Deploy to production with Supabase credentials

## Security Best Practices

1. ✅ Never expose `SUPABASE_SERVICE_KEY` to client-side code
2. ✅ Use Row Level Security (RLS) policies (already configured!)
3. ✅ Rotate API keys if compromised
4. ✅ Enable database backups in production
5. ✅ Monitor usage in Supabase dashboard

For questions or issues, check:
- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Discord](https://discord.supabase.com)
