"""Esquema inicial: las 5 tablas de la sección 3 del readme (db-01-esquema).

Autogenerada y revisada a mano (design D2): CHECK con nombre, server_default y orden de
creación según las FK. El downgrade elimina las tablas en orden inverso.

Revision ID: 0001
Revises: 
Create Date: 2026-11-25 13:09:37.362870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crea las 5 tablas con sus restricciones e índices."""
    op.create_table('cobertura_precio',
    sa.Column('ticker', sa.String(length=10), nullable=False),
    sa.Column('desde', sa.Date(), nullable=False),
    sa.Column('hasta', sa.Date(), nullable=False),
    sa.Column('actualizado_en', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('ultimo_split', sa.Date(), nullable=True),
    sa.CheckConstraint("ticker ~ '^[A-Z.-]{1,10}$'", name=op.f('ck_cobertura_precio_ticker')),
    sa.CheckConstraint('hasta >= desde', name=op.f('ck_cobertura_precio_rango')),
    sa.PrimaryKeyConstraint('ticker', name=op.f('pk_cobertura_precio'))
    )
    op.create_table('importacion',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('fichero_sha256', sa.CHAR(length=64), nullable=False),
    sa.Column('importada_en', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_importacion'))
    )
    op.create_index(op.f('ix_importacion_fichero_sha256'), 'importacion', ['fichero_sha256'], unique=False)
    op.create_table('precio_diario',
    sa.Column('ticker', sa.String(length=10), nullable=False),
    sa.Column('fecha', sa.Date(), nullable=False),
    sa.Column('apertura', sa.Numeric(precision=18, scale=6), nullable=False),
    sa.Column('maximo', sa.Numeric(precision=18, scale=6), nullable=False),
    sa.Column('minimo', sa.Numeric(precision=18, scale=6), nullable=False),
    sa.Column('cierre', sa.Numeric(precision=18, scale=6), nullable=False),
    sa.Column('cierre_sin_ajustar', sa.Numeric(precision=18, scale=6), nullable=False),
    sa.Column('fuente', sa.String(), nullable=False),
    sa.Column('obtenido_en', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("fuente IN ('yfinance', 'ficheros')", name=op.f('ck_precio_diario_fuente')),
    sa.CheckConstraint("ticker ~ '^[A-Z.-]{1,10}$'", name=op.f('ck_precio_diario_ticker')),
    sa.CheckConstraint('apertura > 0', name=op.f('ck_precio_diario_apertura')),
    sa.CheckConstraint('cierre > 0', name=op.f('ck_precio_diario_cierre')),
    sa.CheckConstraint('cierre_sin_ajustar > 0', name=op.f('ck_precio_diario_cierre_sin_ajustar')),
    sa.CheckConstraint('maximo > 0', name=op.f('ck_precio_diario_maximo')),
    sa.CheckConstraint('maximo >= minimo', name=op.f('ck_precio_diario_maximo_minimo')),
    sa.CheckConstraint('minimo > 0', name=op.f('ck_precio_diario_minimo')),
    sa.PrimaryKeyConstraint('ticker', 'fecha', name=op.f('pk_precio_diario'))
    )
    op.create_table('cartera_vigente',
    sa.Column('id', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('importacion_id', sa.Uuid(), nullable=False),
    sa.Column('actualizada_en', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('id', name=op.f('ck_cartera_vigente_una_fila')),
    sa.ForeignKeyConstraint(['importacion_id'], ['importacion.id'], name=op.f('fk_cartera_vigente_importacion_id_importacion'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_cartera_vigente')),
    sa.UniqueConstraint('importacion_id', name=op.f('uq_cartera_vigente_importacion_id'))
    )
    op.create_table('posicion',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('importacion_id', sa.Uuid(), nullable=False),
    sa.Column('fila', sa.Integer(), nullable=False),
    sa.Column('ticker', sa.String(length=10), nullable=False),
    sa.Column('fecha_compra', sa.Date(), nullable=False),
    sa.Column('cantidad', sa.Numeric(precision=18, scale=6), nullable=False),
    sa.Column('precio_compra', sa.Numeric(precision=18, scale=6), nullable=False),
    sa.Column('fecha_venta', sa.Date(), nullable=True),
    sa.Column('precio_venta', sa.Numeric(precision=18, scale=6), nullable=True),
    sa.CheckConstraint("ticker ~ '^[A-Z.-]{1,10}$'", name=op.f('ck_posicion_ticker')),
    sa.CheckConstraint('(fecha_venta IS NULL) = (precio_venta IS NULL)', name=op.f('ck_posicion_venta_completa')),
    sa.CheckConstraint('cantidad > 0', name=op.f('ck_posicion_cantidad')),
    sa.CheckConstraint('fecha_venta >= fecha_compra', name=op.f('ck_posicion_venta_posterior')),
    sa.CheckConstraint('fila >= 2', name=op.f('ck_posicion_fila')),
    sa.CheckConstraint('precio_compra > 0', name=op.f('ck_posicion_precio_compra')),
    sa.CheckConstraint('precio_venta > 0', name=op.f('ck_posicion_precio_venta')),
    sa.ForeignKeyConstraint(['importacion_id'], ['importacion.id'], name=op.f('fk_posicion_importacion_id_importacion'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_posicion')),
    sa.UniqueConstraint('importacion_id', 'fila', name=op.f('uq_posicion_importacion_id_fila'))
    )
    op.create_index(op.f('ix_posicion_importacion_id_ticker'), 'posicion', ['importacion_id', 'ticker'], unique=False)


def downgrade() -> None:
    """Elimina las 5 tablas."""
    op.drop_index(op.f('ix_posicion_importacion_id_ticker'), table_name='posicion')
    op.drop_table('posicion')
    op.drop_table('cartera_vigente')
    op.drop_table('precio_diario')
    op.drop_index(op.f('ix_importacion_fichero_sha256'), table_name='importacion')
    op.drop_table('importacion')
    op.drop_table('cobertura_precio')
