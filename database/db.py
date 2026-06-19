from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Date
from sqlalchemy import Text  # <-- Agregado para permitir descripciones largas
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


# =====================================================
# CREAR BASE DE DATOS
# =====================================================

engine = create_engine(
    "sqlite:///database/cocoya.db",
    echo=False
)

# =====================================================
# BASE
# =====================================================

Base = declarative_base()

# =====================================================
# TABLA PEDIDOS
# =====================================================

class Pedido(Base):

    __tablename__ = "pedidos"

    id = Column(
        Integer,
        primary_key=True
    )

    cliente = Column(String)

    telefono = Column(String)

    identificacion = Column(String)

    producto = Column(String)

    cantidad = Column(Integer)

    valor_total = Column(Float)

    abono = Column(Float)

    saldo = Column(Float)

    estado_pago = Column(String)

    sinpe = Column(String)

    fecha_pedido = Column(Date)

    fecha_entrega = Column(Date)

    prioridad = Column(String)

    provincia = Column(String)

    canton = Column(String)

    distrito = Column(String)

    zona = Column(String)

    direccion = Column(String)

    estado = Column(String)

    # =================================================
    # TELAS PERSONALIZADAS
    # =================================================

    tela_personalizada = Column(String)

    imagen_tela = Column(String)

    # =================================================
    # DETALLES ADICIONALES
    # =================================================

    descripcion = Column(Text)  # <-- CORRECCIÓN: Aquí mapeamos la nueva columna en Python


# =====================================================
# CREAR TABLAS
# =====================================================

Base.metadata.create_all(engine)

# =====================================================
# SESIONES
# =====================================================

Session = sessionmaker(bind=engine)

session = Session()