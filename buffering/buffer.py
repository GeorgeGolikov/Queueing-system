from typing import Any
from order.order import Order
from buffering.buffer_placement_manager import BufferPlacementManager


class Buffer:
    # Singleton
    __instance = None

    def __init__(self, volume):
        if not Buffer.__instance:
            print(" buffer __init__ method called..")
            self.__volume = volume
            self.__orders = [None] * volume
            self.__orders_amount_now = 0
            self.__rejected_orders_amount = 0
        else:
            print("Instance already created:", self.get_instance(volume))

    @classmethod
    def get_instance(cls, volume):
        if not cls.__instance:
            cls.__instance = Buffer(volume)
        return cls.__instance

    def is_empty(self):
        return self.__orders_amount_now == 0

    def is_full(self):
        return self.__orders_amount_now == self.__volume

    def reject_order(self, pos, time):
        if isinstance(pos, int) and 0 <= pos < self.__volume:
            self.__orders[pos].set_time_out(time)
            self.__orders[pos].set_time_out_of_buffer(time)
            self.shift_orders(pos)
            self.__rejected_orders_amount += 1
        else:
            raise IndexError

    def shift_orders(self, pos):
        ord_am = self.__orders_amount_now
        if isinstance(pos, int) and 0 <= pos < ord_am:
            for i in range(pos, ord_am - 1):
                self.__orders[i] = self.__orders[i+1]
                self.__orders[i].set_pos_in_buffer(i)
            self.__orders[ord_am - 1] = None
            self.__orders_amount_now -= 1
        else:
            raise IndexError

    # each order goes through the buffer first, even if we have free workers
    def add_order(self, order):
        if isinstance(order, Order):
            pos = BufferPlacementManager.find_place_in_buffer(self)
            if pos is not None:
                order.set_time_got_buffered(order.get_time_in())
                order.set_pos_in_buffer(pos)
                self.__orders[pos] = order
                self.__orders_amount_now += 1
                return True
            else:
                pos_reject = BufferPlacementManager.find_order_to_reject(self, order)
                if pos_reject is not None:
                    time = order.get_time_in()
                    self.reject_order(pos_reject, time)
                    order.set_time_got_buffered(time)
                    order.set_pos_in_buffer(self.__orders_amount_now)
                    self.__orders[self.__orders_amount_now] = order
                    self.__orders_amount_now += 1
                    return True
                else:
                    order.set_time_out(order.get_time_in())
                    self.__rejected_orders_amount += 1
                    return False
        else:
            raise TypeError("Given argument is not Order type!")

    def set_volume(self, volume):
        self.__volume = volume

    def get_volume(self):
        return self.__volume

    def get_orders(self):
        return self.__orders

    def get_orders_amount_now(self):
        return self.__orders_amount_now

    def get_rejected_orders_amount(self):
        return self.__rejected_orders_amount
