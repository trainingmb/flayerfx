#!/usr/bin/python3
"""
Module: console
This module defines a command-line interface (CLI) for managing instances of Store, Product, and Price classes. It provides various commands to create, show, update, and delete instances, as well as to perform specific queries.
Classes:
    FLYRFXCommand: A class representing the command interpreter for the FLAYERFX console.
Public Functions:
    do_EOF(arg): Exits the console.
    emptyline(): Overwrites the emptyline method to do nothing.
    do_exit(arg): Quit command to exit the program.
    do_quit(arg): Quit command to exit the program.
    _key_value_parser(args): Creates a dictionary from a list of strings.
    do_fields(arg): Prints the fields for a specified class.
    do_create(arg): Creates a new instance of a class.
    do_show(arg): Prints an instance as a string based on the class and id.
    do_destroy(arg): Deletes an instance based on the class and id.
    do_all(arg): Prints string representations of instances.
    do_update(arg): Updates an instance based on the class name, id, attribute, and value.
    do_products(arg): Provides a list of all products in a store.
    do_search(arg): Searches for a product by name.
    do_price_history(arg): Gets the price history of a specific product.
Usage:
    This module is used to interact with and manage instances of Store, Product, and Price classes via a command-line interface.
    Example:
        $ python console.py
        (flayerfx) create Store name="My Store"
        (flayerfx) show Store 1234
        (flayerfx) update Product 5678 name="New Product Name"
        (flayerfx) all Store
"""

import cmd
import shlex  # for splitting the line along spaces except in double quotes
from datetime import datetime

import models
from models.class_store import *

class FLYRFXCommand(cmd.Cmd):
    """ FLAYERFX console """
    prompt = '(flayerfx) '

    def do_EOF(self, arg):
        """Exits console"""
        return True

    def emptyline(self):
        """ overwriting the emptyline method """
        return False

    def do_exit(self, arg):
        """Quit command to exit the program"""
        return True

    def do_quit(self, arg):
        """Quit command to exit the program"""
        return True

    def _key_value_parser(self, args):
        """creates a dictionary from a list of strings"""
        new_dict = {}
        for arg in args:
            if "=" in arg:
                kvp = arg.split('=', 1)
                key = kvp[0]
                value = kvp[1]
                print(key, value)
                if value[0] == value[-1] == '"':
                    value = shlex.split(value)[0].replace('_', ' ')
                else:
                    try:
                        value = int(value)
                    except:
                        try:
                            value = float(value)
                        except:
                            continue
                new_dict[key] = value
        return new_dict

    def do_fields(self, arg):
        """Get Fields for a class"""
        args = arg.split()
        if len(args) == 0:
            print("** class name missing **")
            return False
        if args[0] in classes:
            flds = fields[args[0]]
        else:
            print("** class doesn't exist **")
            return False
        for value in flds:
            print('{}<{}>:\n\t{}'.format(value[0],value[1],value[2]))

    def do_create(self, arg):
        """Creates a new instance of a class"""
        args = arg.split()
        if len(args) == 0:
            print("** class name missing **")
            return False
        if args[0] in classes:
            new_dict = self._key_value_parser(args[1:])
            instance = classes[args[0]](**new_dict)
        else:
            print("** class doesn't exist **")
            return False
        print(instance.id)
        instance.save()

    def do_show(self, arg):
        """Prints an instance as a string based on the class and id"""
        args = shlex.split(arg)
        if len(args) == 0:
            print("** class name missing **")
            return False
        if args[0] in classes:
            if len(args) > 1:
                key = args[0] + "." + args[1]
                if key in models.storage.all():
                    print(models.storage.all()[key])
                else:
                    print("** no instance found **")
            else:
                print("** instance id missing **")
        else:
            print("** class doesn't exist **")

    def do_destroy(self, arg):
        """Deletes an instance based on the class and id"""
        args = shlex.split(arg)
        if len(args) == 0:
            print("** class name missing **")
        elif args[0] in classes:
            if len(args) > 1:
                key = args[0] + "." + args[1]
                if key in models.storage.all():
                    models.storage.all().pop(key)
                    models.storage.save()
                else:
                    print("** no instance found **")
            else:
                print("** instance id missing **")
        else:
            print("** class doesn't exist **")

    def do_all(self, arg):
        """Prints string representations of instances"""
        args = shlex.split(arg)
        obj_list = []
        if len(args) == 0:
            obj_dict = models.storage.all()
        elif args[0] in classes:
            obj_dict = models.storage.all(classes[args[0]])
        else:
            print("** class doesn't exist **")
            return False
        for key in obj_dict:
            obj_list.append(str(obj_dict[key]))
        print("[", end="")
        print(", \n".join(obj_list), end="")
        print("]")

    def do_update(self, arg):
        """Update an instance based on the class name, id, attribute & value"""
        args = shlex.split(arg)
        integers = ["reference"]
        floats = ["amount"]
        if len(args) == 0:
            print("** class name missing **")
        elif args[0] in classes:
            if len(args) > 1:
                k = args[0] + "." + args[1]
                if k in models.storage.all():
                    if len(args) > 2:
                        if len(args) > 3:
                            if True:
                                if args[2] in integers:
                                    try:
                                        args[3] = int(args[3])
                                    except:
                                        args[3] = 0
                                elif args[2] in floats:
                                    try:
                                        args[3] = float(args[3])
                                    except:
                                        args[3] = 0.0
                            setattr(models.storage.all()[k], args[2], args[3])
                            models.storage.all()[k].save()
                        else:
                            print("** value missing **")
                    else:
                        print("** attribute name missing **")
                else:
                    print("** no instance found **")
            else:
                print("** instance id missing **")
        else:
            print("** class doesn't exist **")

    def do_products(self, arg):
        """Provides a list of all products in a store"""
        args = shlex.split(arg)
        store = None
        if len(args) == 0:
            print("** Store ID Missing **")
            return
        elif len(args) == 1:
            dic = {'id': args[0]}
            store = models.storage.get(Store, **dic)
        elif len(args) > 1:
            dic = {args[0]: args[1]}
            store = models.storage.get(Store, **dic)
        if store is not None:
            if len(store) > 1:
                print("** Multiple Stores Found **")
                return
            store = store[0]
            print(f"{store.name} Products({len(store.products)})")
            count = 0
            for item in store.products:
                lp = item.latest_price
                if lp is not None:
                    print(f"{item.name}\t({lp.amount})")
                else:
                    print(f"{item.name}\t(?)")
                count = count + 1
                if count%10 == 0  and input() in ['x', 'X', 'c', 'C']:
                    break
        else:
            print("** No Store Found **")

    def do_search(self, arg):
        """Search for a product by name"""
        args = shlex.split(arg)
        prod = None
        print(args)
        if len(args) == 0:
            print("** Product Name Missing **")
            return
        elif len(args) == 1:
            dic = {
                'name': args[0]
            }
            prod = models.storage.search(Product, **dic)
        elif len(args) == 2:
            dic = {
                'name': args[0],
                'store_id': args[1]
            }
            prod = models.storage.search(Product, **dic)
        if prod is None:
            print("** No Product Found **")
        else:
            prod = sorted(prod, key = lambda i: i.store_id)
            storeid = None
            for item in prod:
                if storeid != item.store_id:
                    storeid = item.store_id
                    print(f"\n**{item.store.name}**")
                lp = item.latest_price
                if lp is not None:
                    print(f"{item.name}\t({lp.amount})")
                else:
                    print(f"{item.name}\t(?)")
    def do_price_history(self, arg):
        """Get prices af a specific product:
            prices <product id> (<limit>)
        """
        #TODO: Finish this
        args = shlex.split(arg)
        prod = None
        if len(args) == 0:
            print("** Product ID Missing **")
            return
        elif len(args) == 1:
            dic = {
                'id': args[0]
            }
            prod = models.storage.get(Product, **dic)
        if prod is None:
            print("** No Product Found **")
        else:
            prod = prod[0]
            for price in prod.prices_sorted:
                print(f"{price.fetched_at}-{price.amount}")


if __name__ == '__main__':
    FLYRFXCommand().cmdloop()