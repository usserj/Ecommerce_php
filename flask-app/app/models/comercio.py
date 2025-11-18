"""Commerce/Store configuration model."""
from app.extensions import db


class Comercio(db.Model):
    """Commerce settings model."""

    __tablename__ = 'comercio'

    id = db.Column(db.Integer, primary_key=True)
    impuesto = db.Column(db.Float, default=0)  # Tax rate
    envioNacional = db.Column(db.Float, default=0)  # National shipping cost
    envioInternacional = db.Column(db.Float, default=0)  # International shipping cost
    tasaMinimaNal = db.Column(db.Float, default=0)  # Minimum rate for national shipping
    tasaMinimaInt = db.Column(db.Float, default=0)  # Minimum rate for international shipping
    pais = db.Column(db.String(100), default='')  # Default country

    # PayPal configuration
    modoPaypal = db.Column(db.String(20), default='sandbox')  # sandbox or live
    clienteIdPaypal = db.Column(db.Text)
    llaveSecretaPaypal = db.Column(db.Text)

    # PayU configuration
    modoPayu = db.Column(db.String(20), default='test')  # test or live
    merchantIdPayu = db.Column(db.Integer, default=0)
    accountIdPayu = db.Column(db.Integer, default=0)
    apiKeyPayu = db.Column(db.Text)

    def __repr__(self):
        return f'<Comercio {self.id}>'

    @staticmethod
    def get_config():
        """Get commerce configuration (singleton)."""
        config = Comercio.query.first()
        if not config:
            config = Comercio()
            db.session.add(config)
            db.session.commit()
        return config

    def calculate_tax(self, amount):
        """Calculate tax for given amount."""
        return amount * (self.impuesto / 100)

    def calculate_shipping(self, country):
        """Calculate shipping cost based on country."""
        if country.lower() == self.pais.lower():
            return self.envioNacional
        return self.envioInternacional

    def get_paypal_config(self):
        """Get PayPal configuration."""
        return {
            'mode': self.modoPaypal,
            'client_id': self.clienteIdPaypal,
            'client_secret': self.llaveSecretaPaypal
        }

    def get_payu_config(self):
        """Get PayU configuration."""
        return {
            'mode': self.modoPayu,
            'merchant_id': self.merchantIdPayu,
            'account_id': self.accountIdPayu,
            'api_key': self.apiKeyPayu
        }
