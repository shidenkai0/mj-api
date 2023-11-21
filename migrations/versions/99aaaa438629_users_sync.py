"""users sync.

Revision ID: 99aaaa438629
Revises: 29033ae4a562
Create Date: 2023-11-20 09:58:42.911998

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99aaaa438629'
down_revision = '29033ae4a562'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Mock the auth schema and auth.users table if it doesn't exist
    op.execute(
        """
        CREATE SCHEMA IF NOT EXISTS auth;
        """
    )
    # We may need to add more columns to this mock table in the future
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS auth.users (
            id uuid NOT NULL,
            email text NULL,
            raw_user_meta_data jsonb NULL,
            CONSTRAINT users_pkey PRIMARY KEY (id)
        );
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.handle_auth_user_change()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO public.user (supabase_uid, email, name, is_superuser)
                VALUES (NEW.id, NEW.email, '', false);
            ELSIF TG_OP = 'UPDATE' THEN
                UPDATE public.user
                SET email = NEW.email
                WHERE supabase_uid = NEW.id;
            ELSIF TG_OP = 'DELETE' THEN
                DELETE FROM public.user
                WHERE supabase_uid = OLD.id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trigger_auth_user_change
        AFTER INSERT OR UPDATE OR DELETE ON auth.users
        FOR EACH ROW EXECUTE FUNCTION public.handle_auth_user_change();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER trigger_auth_user_change ON auth.users;")
    op.execute("DROP FUNCTION public.handle_auth_user_change();")
