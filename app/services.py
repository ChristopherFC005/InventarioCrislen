from decimal import Decimal, InvalidOperation
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.database import SessionLocal
from app.models import InventoryMovement, MovementType, Product, Variant

class InventoryError(ValueError): pass

class InventoryService:
    def crear_producto(self, nombre, categoria, stock_minimo, descripcion=""):
        if not nombre.strip() or not categoria.strip() or stock_minimo < 0: raise InventoryError("Completa nombre, categoría y stock mínimo válido.")
        with SessionLocal.begin() as s:
            if s.scalar(select(Product).where(Product.nombre == nombre.strip())): raise InventoryError("Ya existe un producto con ese nombre.")
            item = Product(nombre=nombre.strip(), categoria=categoria.strip(), stock_minimo=stock_minimo, descripcion=descripcion.strip() or None); s.add(item)
        return item
    def crear_variante(self, producto_id, sku, talla, color, precio, stock_inicial):
        try: precio_decimal = Decimal(precio)
        except (InvalidOperation, ValueError): raise InventoryError("El precio no es válido.")
        if not sku.strip() or not talla.strip() or not color.strip() or precio_decimal < 0 or stock_inicial < 0: raise InventoryError("Completa SKU, talla, color, precio y stock inicial válidos.")
        with SessionLocal.begin() as s:
            if not s.get(Product, producto_id): raise InventoryError("El producto no existe.")
            if s.scalar(select(Variant).where(Variant.sku == sku.strip().upper())): raise InventoryError("El SKU debe ser único.")
            item=Variant(producto_id=producto_id,sku=sku.strip().upper(),talla=talla.strip().upper(),color=color.strip().title(),precio_venta=precio_decimal,stock_actual=stock_inicial); s.add(item); s.flush()
            if stock_inicial: s.add(InventoryMovement(variante_id=item.id,tipo=MovementType.ENTRADA,cantidad=stock_inicial,motivo="Stock inicial",referencia="INICIAL"))
        return item
    def eliminar_producto(self, producto_id):
        """Elimina un producto, sus variantes y su historial de movimientos."""
        with SessionLocal.begin() as s:
            producto = s.get(Product, producto_id)
            if not producto:
                raise InventoryError("El producto seleccionado ya no existe.")
            s.delete(producto)
    def registrar_movimiento(self, variante_id, tipo, cantidad, motivo, referencia=""):
        try: clase=MovementType(tipo)
        except ValueError: raise InventoryError("Tipo de movimiento inválido.")
        if cantidad <= 0 or not motivo.strip(): raise InventoryError("Cantidad mayor a cero y motivo obligatorio.")
        with SessionLocal.begin() as s:
            item=s.get(Variant,variante_id,with_for_update=True)
            if not item: raise InventoryError("La variante no existe.")
            delta=cantidad if clase in (MovementType.ENTRADA,MovementType.AJUSTE) else -cantidad
            if item.stock_actual + delta < 0: raise InventoryError(f"Stock insuficiente. Disponible: {item.stock_actual}.")
            item.stock_actual += delta; s.add(InventoryMovement(variante_id=item.id,tipo=clase,cantidad=cantidad,motivo=motivo.strip(),referencia=referencia.strip() or None))
    def productos(self):
        with SessionLocal() as s: return s.scalars(select(Product).options(joinedload(Product.variantes)).order_by(Product.nombre)).unique().all()
    def variantes(self):
        with SessionLocal() as s: return s.scalars(select(Variant).options(joinedload(Variant.producto)).order_by(Variant.sku)).all()
    def movimientos(self, limite=100):
        with SessionLocal() as s: return s.scalars(select(InventoryMovement).options(joinedload(InventoryMovement.variante).joinedload(Variant.producto)).order_by(InventoryMovement.creado_en.desc()).limit(limite)).all()
    def resumen(self):
        variantes=self.variantes(); bajos=[x for x in variantes if x.stock_actual <= x.producto.stock_minimo]
        return {"productos":len(self.productos()),"variantes":len(variantes),"unidades":sum(x.stock_actual for x in variantes),"bajos":bajos}
