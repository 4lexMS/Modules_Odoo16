/** @odoo-module */

import { Order} from 'point_of_sale.models';
import Registries from "point_of_sale.Registries";

const PosCustomerDiscountsOrder = (Order) =>
class extends Order{
    constructor(obj, options) {
        super(...arguments);
        this.vip_discounts  = this.vip_discounts || false;
    }
    check_birthday_partner(){
        const currentPartner = this.get_partner();
        if (currentPartner && currentPartner.birthday && currentPartner.is_vip_customer && this.pos.config.customer_discounts){
            var today = new Date();
            var birthday = new Date(currentPartner.birthday);

            if (today.getMonth() === birthday.getUTCMonth() && today.getDate() === birthday.getUTCDate()){
                return true
                }
            }
        return false
    }
    set_discount_partner_birthday(){
        var orderLines = this.orderlines;
        var discount = 0
        if(this.check_birthday_partner()){
            discount = this.pos.config.discount_birthday * 100
        }
        for (var order_id = 0; order_id < orderLines.length; order_id++) {
            orderLines[order_id].set_discount(discount);
        }
    }
    add_product(product, options) {
        super.add_product(...arguments);
        var orderline = this.get_selected_orderline();
        if (orderline && this.check_birthday_partner()){
            var discount = this.pos.config.discount_birthday * 100
            orderline.set_discount(discount)
        }
    }

    add_paymentline(payment_method){
        const currentPartner = this.get_partner();
        if (currentPartner && currentPartner.is_vip_customer && this.pos.config.customer_discounts && this.get_total_discount() == 0 ){
            var discount = 0
            if (payment_method.is_cash_count){
                discount = this.pos.config.discount_cash_payment * 100
            }else if (!payment_method.journal_id){
                discount = this.pos.config.discount_card_payment * 100
            }
            if (discount != 0){
                this.vip_discounts = true
                var orderLines = this.orderlines;
                for (var order_id = 0; order_id < orderLines.length; order_id++) {
                    orderLines[order_id].set_discount(discount);
                }
            }
        }
        return super.add_paymentline(...arguments);
    }

    remove_paymentline(line){
        super.remove_paymentline(...arguments);
        if (this.vip_discounts){
            var orderLines = this.orderlines;
            for (var order_id = 0; order_id < orderLines.length; order_id++) {
                orderLines[order_id].set_discount(0);
            }
        }
    }
}
Registries.Model.extend(Order, PosCustomerDiscountsOrder);
