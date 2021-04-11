"""setup database

Revision ID: f7c982786f3f
Revises:
Create Date: 2021-04-09 20:06:24.234858

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7c982786f3f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('displayname', sa.String(length=64), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='fitness',
    comment='Stores user login details'
    )
    op.create_index(op.f('ix_fitness_user_email'), 'user', ['email'], unique=True, schema='fitness')
    op.create_table('workout',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(length=50), nullable=False),
    sa.Column('wrkt_dttm', sa.DateTime(), nullable=False),
    sa.Column('dur_sec', sa.Integer(), nullable=True),
    sa.Column('dist_mi', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('pace_sec', sa.Integer(), nullable=True),
    sa.Column('gear', sa.String(length=50), nullable=True),
    sa.Column('clothes', sa.Text(), nullable=True),
    sa.Column('ele_up', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('ele_down', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('hr', sa.SmallInteger(), nullable=True),
    sa.Column('cal_burn', sa.Integer(), nullable=True),
    sa.Column('category', sa.String(length=50), nullable=True),
    sa.Column('location', sa.String(length=50), nullable=True),
    sa.Column('training_type', sa.String(length=50), nullable=True),
    sa.Column('temp_strt', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('temp_feels_like_strt', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('wethr_cond_strt', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('hmdty_strt', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('wind_speed_strt', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('wind_gust_strt', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('temp_end', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('temp_feels_like_end', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('wethr_cond_end', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('hmdty_end', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('wind_speed_end', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('wind_gust_end', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('warm_up_tot_dist_mi', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('warm_up_tot_tm_sec', sa.Integer(), nullable=True),
    sa.Column('warm_up_tot_pace_sec', sa.Integer(), nullable=True),
    sa.Column('cool_down_tot_dist_mi', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('cool_down_tot_tm_sec', sa.Integer(), nullable=True),
    sa.Column('cool_down_tot_pace_sec', sa.Integer(), nullable=True),
    sa.Column('intrvl_tot_dist_mi', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('intrvl_tot_tm_sec', sa.Integer(), nullable=True),
    sa.Column('intrvl_tot_pace_sec', sa.Integer(), nullable=True),
    sa.Column('intrvl_tot_ele_up', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('intrvl_tot_ele_down', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('isrt_ts', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['fitness.user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='fitness',
    comment='Store Workout data'
    )
    op.create_index(op.f('ix_fitness_workout_isrt_ts'), 'workout', ['isrt_ts'], unique=False, schema='fitness')
    op.create_index(op.f('ix_fitness_workout_type'), 'workout', ['type'], unique=False, schema='fitness')
    op.create_index(op.f('ix_fitness_workout_wrkt_dttm'), 'workout', ['wrkt_dttm'], unique=False, schema='fitness')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_fitness_workout_wrkt_dttm'), table_name='workout', schema='fitness')
    op.drop_index(op.f('ix_fitness_workout_type'), table_name='workout', schema='fitness')
    op.drop_index(op.f('ix_fitness_workout_isrt_ts'), table_name='workout', schema='fitness')
    op.drop_table('workout', schema='fitness')
    op.drop_index(op.f('ix_fitness_user_email'), table_name='user', schema='fitness')
    op.drop_table('user', schema='fitness')
    # ### end Alembic commands ###