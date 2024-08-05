/** @odoo-module **/

import ProductScreen from 'point_of_sale.ProductScreen';
import Registries from 'point_of_sale.Registries';

export const PosCustomerDiscountsProductScreen = (ProductScreen) =>
    class extends ProductScreen {
        async onClickPartner() {
            await super.onClickPartner();
            this.currentOrder.set_discount_partner_birthday();
        }
    };
Registries.Component.extend(ProductScreen, PosCustomerDiscountsProductScreen);
