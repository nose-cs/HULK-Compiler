#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define OBJECT_DICT_CAPACITY 67

#define bool int
#define true 1
#define false 0

/////////////////////////////////  Types   ////////////////////////////////////

typedef struct Attribute
{
    char* key;
    void* value;
    struct Attribute* next;
} Attribute;
 
typedef struct Object {
    Attribute** lists;
} Object;

unsigned int hash(char* key, int capacity) {
    unsigned long hash = 5381;
    int c;

    while ((c = *key++))
        hash = ((hash << 5) + hash) + c; /* hash * 33 + c */

    return hash % capacity;
}

void addAttribute(Object* obj, char* key, void* value) {
    unsigned int index = hash(key, OBJECT_DICT_CAPACITY);
    Attribute* newAtt = malloc(sizeof(Attribute));
    newAtt->key = strdup(key);
    newAtt->value = value;
    newAtt->next = obj->lists[index];
    obj->lists[index] = newAtt;
}

void* getAttributeValue(Object* obj, char* key) {
    unsigned int index = hash(key, OBJECT_DICT_CAPACITY);
    Attribute* current = obj->lists[index];

    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            return current->value;
        }
        current = current->next;
    }
    
    return NULL;
}

Attribute* getAttribute(Object* obj, char* key) {
    unsigned int index = hash(key, OBJECT_DICT_CAPACITY);
    Attribute* current = obj->lists[index];

    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            return current;
        }
        current = current->next;
    }
    
    return NULL;
}

void replaceAttribute(Object* obj, char* key, void* value) {
    Attribute* att = getAttribute(obj, key);
    free(att->value);
    att->value = value;
}

void removeAttribute(Object* obj, char* key) {
    unsigned int index = hash(key, OBJECT_DICT_CAPACITY);
    Attribute* current = obj->lists[index];
    Attribute* previous = NULL;

    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            if (previous == NULL) {
                obj->lists[index] = current->next;
            } else {
                previous->next = current->next;
            }
            free(current->key);
            free(current->value);
            free(current);
            return;
        }
        previous = current;
        current = current->next;
    }
}


/////////////////////////////////  Method Declaration   ////////////////////////////////////

// Object
Object* createObject();
Object* replaceObject(Object* obj1, Object* obj2);
Object* method_Object_equals(Object* obj1, Object* obj2);
Object* method_Object_toString(Object* obj);

// Protocol
void* getMethodForCurrentType(Object* obj, char* method_name, int index);

// Print
Object* function_print(Object* obj);

// Number
Object* createNumber(double number);
Object* method_Number_toString(Object* number);
Object* method_Number_equals(Object* number1, Object* number2);
Object* numberSum(Object* number1, Object* number2);
Object* numberMinus(Object* number1, Object* number2);
Object* numberMultiply(Object* number1, Object* number2);
Object* numberDivision(Object* number1, Object* number2);
Object* numberPow(Object* number1, Object* number2);
Object* numberParse(Object* string);

// String
Object* createString(char* str);
Object* method_String_toString(Object* str);
Object* method_String_equals(Object* string1, Object* string2);

// Bool
Object* createBool(bool boolean);
Object* method_Bool_toString(Object* boolean);
Object* method_Bool_equals(Object* bool1, Object* bool2);
Object* invertBool(Object* boolean);


/////////////////////////////////  Object   ////////////////////////////////////

Object* createObject() {
    Object* obj = malloc(sizeof(Object));
    
    obj->lists = malloc(sizeof(Attribute*) * OBJECT_DICT_CAPACITY);
    for (int i = 0; i < OBJECT_DICT_CAPACITY; i++) {
        obj->lists[i] = NULL;
    }

    addAttribute(obj, "method_Object_toString", *method_Object_toString);
    addAttribute(obj, "method_Object_equals", *method_Object_equals);
    return obj;
}

Object* replaceObject(Object* obj1, Object* obj2)
{
    obj1->lists = obj2->lists;
    return obj1;
}

Object* method_Object_equals(Object* obj1, Object* obj2)
{
    return createBool(obj1 == obj2);
}

Object* method_Object_toString(Object* obj)
{
    char* address = malloc(50); 
    sprintf(address, "%p", (void*)obj);

    return createString(address);
}

/////////////////////////////////  Protocol   ////////////////////////////////////

void* getMethodForCurrentType(Object* obj, char* method_name, int index)
{
    char* initial_parent_type = malloc(128);
    sprintf(initial_parent_type, "%s%d", "parent_type", index++);
    char* type = getAttributeValue(obj, initial_parent_type);
    free(initial_parent_type);

    while(type != NULL)
    {
        char* full_name = malloc(128);
        sprintf(full_name, "%s%s%s%s", "method_", type, "_", method_name);

        void* method = getAttributeValue(obj, full_name);

        free(full_name);

        if(method != NULL)
            return method;

        char* parent_type = malloc(128);
        sprintf(parent_type, "%s%d", "parent_type", index++);
        type = getAttributeValue(obj, parent_type);
        free(parent_type);
    }

    return NULL;
}

/////////////////////////////////  Print   ////////////////////////////////////

Object* function_print(Object* obj)
{
    Object* str = ((Object* (*)(Object*))getMethodForCurrentType(obj, "toString", 0))(obj);
    
    char* value = getAttributeValue(str, "value");
    printf("%s\n", value);

    return str;
}


/////////////////////////////////  Number   ////////////////////////////////////

Object* createNumber(double number) {
    Object* obj = createObject();

    double* value = malloc(sizeof(double));
    *value = number;

    addAttribute(obj, "value", value);
    addAttribute(obj, "parent_type0", "Number");
    addAttribute(obj, "parent_type1", "Object");
    addAttribute(obj, "method_Number_toString", *method_Number_toString);
    addAttribute(obj, "method_Number_equals", *method_Number_equals);

    return obj;
}

Object* method_Number_toString(Object* number) {
    double* value = getAttributeValue(number, "value");

    char *str = malloc(30);
    sprintf(str, "%f", *value);
    return createString(str);
}

Object* method_Number_equals(Object* number1, Object* number2) {
    double* value1 = getAttributeValue(number1, "value");
    double* value2 = getAttributeValue(number2, "value");

    return createBool(fabs(*value1 - *value2) < 0.000000001);
}

Object* numberSum(Object* number1, Object* number2) {
    double* value1 = getAttributeValue(number1, "value");
    double* value2 = getAttributeValue(number2, "value");

    return createNumber(*value1 + *value2);
}

Object* numberMinus(Object* number1, Object* number2) {
    double* value1 = getAttributeValue(number1, "value");
    double* value2 = getAttributeValue(number2, "value");

    return createNumber(*value1 - *value2);
}

Object* numberMultiply(Object* number1, Object* number2) {
    double* value1 = getAttributeValue(number1, "value");
    double* value2 = getAttributeValue(number2, "value");

    return createNumber(*value1 * *value2);
}

Object* numberDivision(Object* number1, Object* number2) {
    double* value1 = getAttributeValue(number1, "value");
    double* value2 = getAttributeValue(number2, "value");

    return createNumber(*value1 / *value2);
}

Object* numberGreaterThan(Object* number1, Object* number2) {
    double* value1 = getAttributeValue(number1, "value");
    double* value2 = getAttributeValue(number2, "value");

    return createBool(*value1 > *value2);
}

Object* numberGreaterOrEqualThan(Object* number1, Object* number2) {
    double* value1 = getAttributeValue(number1, "value");
    double* value2 = getAttributeValue(number2, "value");

    return createBool(*value1 >= *value2);
}

Object* numberLessThan(Object* number1, Object* number2) {
    double* value1 = getAttributeValue(number1, "value");
    double* value2 = getAttributeValue(number2, "value");

    return createBool(*value1 < *value2);
}

Object* numberLessOrEqualThan(Object* number1, Object* number2) {
    double* value1 = getAttributeValue(number1, "value");
    double* value2 = getAttributeValue(number2, "value");

    return createBool(*value1 <= *value2);
}

Object* numberPow(Object* number1, Object* number2) {
    double* value1 = getAttributeValue(number1, "value");
    double* value2 = getAttributeValue(number2, "value");

    //return createNumber(pow(*value1, *value2));
    return NULL;
}

Object* numberParse(Object* string) {
    char* value = getAttributeValue(string, "value");
    return createNumber(strtod(value, NULL));
}

/////////////////////////////////  String   ////////////////////////////////////

Object* createString(char* str) {
    Object* obj = createObject();

    addAttribute(obj, "value", str);
    addAttribute(obj, "parent_type0", "String");
    addAttribute(obj, "parent_type1", "Object");

    int *len = malloc(sizeof(int));
    *len = strlen(str);

    addAttribute(obj, "len", len);
    addAttribute(obj, "method_String_toString", *method_String_toString);
    addAttribute(obj, "method_String_equals", *method_String_equals);

    return obj;
}

Object* method_String_toString(Object* str) {
    return str;
}

Object* method_String_equals(Object* string1, Object* string2) {
    char* value1 = getAttributeValue(string1, "value");
    char* value2 = getAttributeValue(string2, "value");

    return createBool(strcmp(value1, value2) == 0);
}

/////////////////////////////////  Bool   ////////////////////////////////////

Object* createBool(bool boolean) {
    Object* obj = createObject();

    bool* value = malloc(sizeof(bool));
    *value = boolean;

    addAttribute(obj, "value", value);
    addAttribute(obj, "parent_type0", "Bool");
    addAttribute(obj, "parent_type1", "Object");
    addAttribute(obj, "method_Bool_toString", *method_Bool_toString);
    addAttribute(obj, "method_Bool_equals", *method_Bool_equals);

    return obj;
}

Object* method_Bool_toString(Object* boolean) {
    bool* value = getAttributeValue(boolean, "value");

    if(*value == true)
        return createString("true");
    else
        return createString("false");
}

Object* method_Bool_equals(Object* bool1, Object* bool2) {
    bool* value1 = getAttributeValue(bool1, "value");
    bool* value2 = getAttributeValue(bool2, "value");

    return createBool(value1 == value2);
}

Object* invertBool(Object* boolean) {
    bool* value = getAttributeValue(boolean, "value");

    return createBool(!*value);
}