#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdarg.h>
#include <time.h>

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
Object* createEmptyObject();
Object* createObject();
Object* replaceObject(Object* obj1, Object* obj2);
Object* method_Object_equals(Object* obj1, Object* obj2);
Object* method_Object_toString(Object* obj);

// Dynamic
void* getMethodForCurrentType(Object* obj, char* method_name, char* base_type);
char* getType(Object* obj);
Object* isType(Object* obj, char* type);
Object* isProtocol(Object* obj, char* protocol);

// Print
Object* function_print(Object* obj);

// Number
Object* createNumber(double number);
Object* copyObject(Object* obj);
Object* method_Number_toString(Object* number);
Object* method_Number_equals(Object* number1, Object* number2);
Object* numberSum(Object* number1, Object* number2);
Object* numberMinus(Object* number1, Object* number2);
Object* numberMultiply(Object* number1, Object* number2);
Object* numberDivision(Object* number1, Object* number2);
Object* numberPow(Object* number1, Object* number2);
Object* function_sqrt(Object* number);
Object* function_sin(Object* angle);
Object* function_cos(Object* angle);
Object* function_exp(Object* number);
Object* function_log(Object* number);
Object* function_rand();
Object* function_parse(Object* string);

// String
Object* createString(char* str);
Object* stringConcat(Object* string1, Object* string2);
Object* method_String_size(Object* self);
Object* method_String_toString(Object* str);
Object* method_String_equals(Object* string1, Object* string2);

// Boolean
Object* createBoolean(bool boolean);
Object* method_Boolean_toString(Object* boolean);
Object* method_Boolean_equals(Object* bool1, Object* bool2);
Object* invertBoolean(Object* boolean);
Object* boolOr(Object* bool1, Object* bool2);
Object* boolAnd(Object* bool1, Object* bool2);

// Vector
Object* createVectorFromList(int num_elements, Object** list);
Object* createVector(int num_elements, ...);
Object* method_Vector_size(Object* self);
Object* method_Vector_next(Object* self);
Object* method_Vector_current(Object* self);
Object* getElementOfVector(Object* vector, Object* index);
Object* method_Vector_toString(Object* vector);
Object* method_Vector_equals(Object* vector1, Object* vector2);
Object* function_range(Object* start, Object* end);

// Range
Object* createRange(Object* min, Object* max);
Object* method_Range_next(Object* self);
Object* method_Range_current(Object* self);
Object* method_Range_toString(Object* range);
Object* method_Range_equals(Object* range1, Object* range2);

/////////////////////////////////  Object   ////////////////////////////////////

Object* createEmptyObject() {
    return malloc(sizeof(Object));
}

Object* copyObject(Object* obj) {
    return replaceObject(createEmptyObject(), obj);
}

Object* createObject() {
    Object* obj = createEmptyObject();
    
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
    return createBoolean(obj1 == obj2);
}

Object* method_Object_toString(Object* obj)
{
    char* address = malloc(50); 
    sprintf(address, "%p", (void*)obj);

    return createString(address);
}

/////////////////////////////////  Dynamic   ////////////////////////////////////


char* getType(Object* obj)
{
    return getAttributeValue(obj, "parent_type0");
}

void* getMethodForCurrentType(Object* obj, char* method_name, char* base_type)
{
    bool found_base_type = base_type == NULL;

    int index = 0;
    char* initial_parent_type = malloc(128);
    sprintf(initial_parent_type, "%s%d", "parent_type", index++);
    char* type = getAttributeValue(obj, initial_parent_type);
    free(initial_parent_type);

    while(type != NULL)
    {
        if(found_base_type || strcmp(type, base_type) == 0)
        {
            found_base_type = true;

            char* full_name = malloc(128);
            sprintf(full_name, "%s%s%s%s", "method_", type, "_", method_name);

            void* method = getAttributeValue(obj, full_name);

            free(full_name);

            if(method != NULL)
                return method;
        }

        char* parent_type = malloc(128);
        sprintf(parent_type, "%s%d", "parent_type", index++);
        type = getAttributeValue(obj, parent_type);
        free(parent_type);
    }

    return NULL;
}

Object* isType(Object* obj, char* type)
{
    int index = 0;
    char* initial_parent_type = malloc(128);
    sprintf(initial_parent_type, "%s%d", "parent_type", index++);
    char* ptype = getAttributeValue(obj, initial_parent_type);
    free(initial_parent_type);

    while(ptype != NULL)
    {
        if(strcmp(ptype, type) == 0)
            return createBoolean(true);

        char* parent_type = malloc(128);
        sprintf(parent_type, "%s%d", "parent_type", index++);
        ptype = getAttributeValue(obj, parent_type);
        free(parent_type);
    }

    return createBoolean(false);
}

Object* isProtocol(Object* obj, char* protocol)
{
    int index = 0;
    char* initial_protocol = malloc(128);
    sprintf(initial_protocol, "%s%d", "conforms_protocol", index++);
    char* pprotocol = getAttributeValue(obj, initial_protocol);
    free(initial_protocol);

    while(pprotocol != NULL)
    {
        if(strcmp(pprotocol, protocol) == 0)
            return createBoolean(true);

        char* cprotocol = malloc(128);
        sprintf(cprotocol, "%s%d", "conforms_protocol", index++);
        pprotocol = getAttributeValue(obj, cprotocol);
        free(cprotocol);
    }

    return createBoolean(false);
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
    if(strcmp(getType(number1), getType(number2)) != 0)
        return createBoolean(false);

    double* value1 = getAttributeValue(number1, "value");
    double* value2 = getAttributeValue(number2, "value");

    return createBoolean(fabs(*value1 - *value2) < 0.000000001);
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

Object* numberPow(Object* number1, Object* number2) {
    double value = *(double*)getAttributeValue(number1, "value");
    double exp = *(double*)getAttributeValue(number2, "value");

    return createNumber(pow(value, exp));
}

Object* function_sqrt(Object* number) {
    double value = *(double*)getAttributeValue(number, "value");

    return createNumber(sqrt(value));
}

Object* function_sin(Object* angle) {
    double vangle = *(double*)getAttributeValue(angle, "value");

    return createNumber(sin(vangle));
}

Object* function_cos(Object* angle) {
    double vangle = *(double*)getAttributeValue(angle, "value");

    return createNumber(cos(vangle));
}

Object* function_exp(Object* number) {
    double value = *(double*)getAttributeValue(number, "value");

    return createNumber(exp(value));
}

Object* function_log(Object* number) {
    double value = *(double*)getAttributeValue(number, "value");

    return createNumber(log(value));
}

Object* function_rand() {
    return createNumber((double)rand() / (RAND_MAX + 1.0));
}

Object* numberGreaterThan(Object* number1, Object* number2) {
    double* value1 = getAttributeValue(number1, "value");
    double* value2 = getAttributeValue(number2, "value");

    return createBoolean(*value1 > *value2);
}

Object* numberGreaterOrEqualThan(Object* number1, Object* number2) {
    double* value1 = getAttributeValue(number1, "value");
    double* value2 = getAttributeValue(number2, "value");

    return createBoolean(*value1 >= *value2);
}

Object* numberLessThan(Object* number1, Object* number2) {
    double* value1 = getAttributeValue(number1, "value");
    double* value2 = getAttributeValue(number2, "value");

    return createBoolean(*value1 < *value2);
}

Object* numberLessOrEqualThan(Object* number1, Object* number2) {
    double* value1 = getAttributeValue(number1, "value");
    double* value2 = getAttributeValue(number2, "value");

    return createBoolean(*value1 <= *value2);
}

Object* numberMod(Object* number1, Object* number2) {
    double* value1 = getAttributeValue(number1, "value");
    double* value2 = getAttributeValue(number2, "value");

    return createNumber(((int)*value1) % ((int)*value2));
}

Object* function_parse(Object* string) {
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
    addAttribute(obj, "method_String_size", *method_String_size);

    return obj;
}

Object* stringConcat(Object* string1, Object* string2)
{
    char* str1 = getAttributeValue(string1, "value");
    int len1 = *(int*)getAttributeValue(string1, "len");

    char* str2 = getAttributeValue(string2, "value");
    int len2 = *(int*)getAttributeValue(string2, "len");

    char* result = malloc((len1 + len2) * sizeof(char));
    sprintf(result, "%s%s", str1, str2);
    return createString(result);
}

Object* method_String_size(Object* self) {
    return createNumber(*(int*)getAttributeValue(self, "len"));
}

Object* method_String_toString(Object* str) {
    return str;
}

Object* method_String_equals(Object* string1, Object* string2) {
    if(strcmp(getType(string1), getType(string2)) != 0)
        return createBoolean(false);

    char* value1 = getAttributeValue(string1, "value");
    char* value2 = getAttributeValue(string2, "value");

    return createBoolean(strcmp(value1, value2) == 0);
}

/////////////////////////////////  Boolean   ////////////////////////////////////

Object* createBoolean(bool boolean) {
    Object* obj = createObject();

    bool* value = malloc(sizeof(bool));
    *value = boolean;

    addAttribute(obj, "value", value);
    addAttribute(obj, "parent_type0", "Boolean");
    addAttribute(obj, "parent_type1", "Object");
    addAttribute(obj, "method_Boolean_toString", *method_Boolean_toString);
    addAttribute(obj, "method_Boolean_equals", *method_Boolean_equals);

    return obj;
}

Object* method_Boolean_toString(Object* boolean) {
    bool* value = getAttributeValue(boolean, "value");

    if(*value == true)
        return createString("true");
    else
        return createString("false");
}

Object* method_Boolean_equals(Object* bool1, Object* bool2) {
    if(strcmp(getType(bool1), getType(bool2)) != 0)
        return createBoolean(false);

    bool* value1 = getAttributeValue(bool1, "value");
    bool* value2 = getAttributeValue(bool2, "value");

    return createBoolean(value1 == value2);
}

Object* invertBoolean(Object* boolean) {
    bool* value = getAttributeValue(boolean, "value");

    return createBoolean(!*value);
}

Object* boolOr(Object* bool1, Object* bool2)
{
    bool vbool1 = *(bool*)getAttributeValue(bool1, "value");
    bool vbool2 = *(bool*)getAttributeValue(bool2, "value");

    return createBoolean(vbool1 || vbool2);
}

Object* boolAnd(Object* bool1, Object* bool2)
{
    bool vbool1 = *(bool*)getAttributeValue(bool1, "value");
    bool vbool2 = *(bool*)getAttributeValue(bool2, "value");

    return createBoolean(vbool1 && vbool2);
}

/////////////////////////////////  Vectors   ////////////////////////////////////

Object* createVectorFromList(int num_elements, Object** list)
{
    Object* vector = createObject();

    addAttribute(vector, "parent_type0", "Vector");
    addAttribute(vector, "parent_type1", "Object");

    addAttribute(vector, "conforms_protocol0", "Iterable");

    addAttribute(vector, "method_Vector_toString", *method_Vector_toString);
    addAttribute(vector, "method_Vector_equals", *method_Vector_equals);

    int* size = malloc(sizeof(int));
    *size = num_elements;
    addAttribute(vector, "size", size);

    addAttribute(vector, "list", list);

    addAttribute(vector, "current", createNumber(-1));

    addAttribute(vector, "method_Vector_size", *method_Vector_size);
    addAttribute(vector, "method_Vector_next", *method_Vector_next);
    addAttribute(vector, "method_Vector_current", *method_Vector_current);

    return vector;
}

Object* createVector(int num_elements, ...)
{
    va_list elements;

    va_start(elements, num_elements);

    Object** list = malloc(num_elements * sizeof(Object*));

    for(int i = 0; i < num_elements; i++) {
        list[i] = va_arg(elements, Object*);
    }

    va_end(elements);

    return createVectorFromList(num_elements, list);
}

Object* method_Vector_size(Object* self) {
    return createNumber(*(int*)getAttributeValue(self, "size"));
}

Object* method_Vector_next(Object* self)
{
    int size = *(int*)getAttributeValue(self, "size");
    double* current = getAttributeValue((Object*)getAttributeValue(self, "current"), "value");
    
    if(*current + 1 < size) 
    {
        *current += 1;
        return createBoolean(true);
    }

    return createBoolean(false);
}

Object* method_Vector_current(Object* self)
{
    return getElementOfVector(self, getAttributeValue(self, "current"));
}

Object* getElementOfVector(Object* vector, Object* index)
{
    return ((Object**)getAttributeValue(vector, "list"))[(int)*(double*)getAttributeValue(index, "value")];
}

Object* method_Vector_toString(Object* vector)
{
    int* size = getAttributeValue(vector, "size");

    int total_size = 3 + ((*size > 0 ? *size : 1) - 1) * 2;

    Object** list = getAttributeValue(vector, "list");

    Object** strs = malloc(*size * sizeof(Object*));

    for(int i = 0; i < *size; i++)
    {
        strs[i] = ((Object* (*)(Object*))getMethodForCurrentType(list[i], "toString", 0))(list[i]);
        total_size += *(int*)getAttributeValue(strs[i], "len");
    }

    char* result = malloc(total_size * sizeof(char));
    result[0] = '\0';

    strcat(result, "[");
    for(int i = 0; i < *size; i++)
    {
        strcat(result, (char*)getAttributeValue(strs[i], "value"));
        free(strs[i]);

        if(i + 1 < *size)
            strcat(result, ", ");
    }
    strcat(result, "]");

    free(strs);

    return createString(result);
}

Object* method_Vector_equals(Object* vector1, Object* vector2)
{
    if(strcmp(getType(vector1), getType(vector2)) != 0)
        return createBoolean(false);

    int* size1 = getAttributeValue(vector1, "size");
    Object** list1 = getAttributeValue(vector1, "list");

    int* size2 = getAttributeValue(vector2, "size");
    Object** list2 = getAttributeValue(vector2, "list");

    if(*size1 != *size2)
        return createBoolean(false);

    for(int i = 0; i < *size1; i++)
    {
        bool* equal = getAttributeValue(((Object* (*)(Object*, Object*))getMethodForCurrentType(list1[i], "equals", 0))(list1[i], list2[i]), "value");

        if(!*equal)
            return createBoolean(false);
    }

    return createBoolean(true);
}


/////////////////////////////////  Range   ////////////////////////////////////

Object* function_range(Object* start, Object* end)
{
    return createRange(start, end);
}

Object* createRange(Object* min, Object* max)
{
    Object* obj = createObject();

    addAttribute(obj, "min", min);
    addAttribute(obj, "max", max);
    addAttribute(obj, "current", numberMinus(min, createNumber(1)));

    addAttribute(obj, "parent_type0", "Range");
    addAttribute(obj, "parent_type1", "Object");

    addAttribute(obj, "conforms_protocol0", "Iterable");

    addAttribute(obj, "method_Range_next", *method_Range_next);
    addAttribute(obj, "method_Range_current", *method_Range_current);

    addAttribute(obj, "method_Range_toString", *method_Range_toString);
    addAttribute(obj, "method_Range_equals", *method_Range_equals);

    return obj;
}

Object* method_Range_next(Object* self)
{
    int max = *(double*)getAttributeValue((Object*)getAttributeValue(self, "max"), "value");
    double* current = getAttributeValue((Object*)getAttributeValue(self, "current"), "value");
    
    if(*current + 1 < max) 
    {
        *current += 1;
        return createBoolean(true);
    }

    return createBoolean(false);
}

Object* method_Range_current(Object* self)
{
    return getAttributeValue(self, "current");
}

Object* method_Range_toString(Object* range)
{
    Object* min = getAttributeValue(range, "min");
    Object* max = getAttributeValue(range, "max");

    int total_size = 6;

    Object* min_str = ((Object* (*)(Object*))getMethodForCurrentType(min, "toString", 0))(min);
    total_size += *(int*)getAttributeValue(min_str, "len");

    Object* max_str = ((Object* (*)(Object*))getMethodForCurrentType(max, "toString", 0))(max);
    total_size += *(int*)getAttributeValue(max_str, "len");

    char* result = malloc(total_size * sizeof(char));
    sprintf(result, "[%s - %s]", (char*)getAttributeValue(min_str, "value"), (char*)getAttributeValue(max_str, "value"));

    free(min_str);
    free(max_str);
    return createString(result);
}

Object* method_Range_equals(Object* range1, Object* range2)
{
    Object* min1 = getAttributeValue(range1, "min");
    Object* max1 = getAttributeValue(range1, "max");

    Object* min2 = getAttributeValue(range2, "min");
    Object* max2 = getAttributeValue(range2, "max");

    return boolAnd(method_Number_equals(min1, min2), method_Number_equals(max1, max2));
}

/////////////////////////////////  Generated Code  ////////////////////////////////////

Object* function_Sort (Object* p0);

Object* letInNode0(Object* p0);

Object* loopBlock0(Object* v0, Object* p0);

Object* loopBlock1(Object* v1, Object* v0, Object* p0);

Object* ifElseBlock0(Object* v2, Object* v1, Object* v0, Object* p0);

Object* letInNode0(Object* p0) {
   Object* v0 = copyObject(createNumber(0));
   return loopBlock0(v0, p0);
}

Object* ifElseBlock0(Object* v2, Object* v1, Object* v0, Object* p0) {
   if(*((bool*)getAttributeValue(numberLessThan(getElementOfVector(p0, v2), getElementOfVector(p0, v1)), "value"))) {
      replaceObject(v0, getElementOfVector(p0, v1));
      replaceObject(getElementOfVector(p0, v1), getElementOfVector(p0, v2));
      replaceObject(getElementOfVector(p0, v2), v0);
      return p0;
   }
   else {
      return p0;
   }
}

Object* loopBlock1(Object* v1, Object* v0, Object* p0) {
   Object* return_obj = NULL;
   Object* v2 = NULL;
   Object* iterable = function_range(copyObject(v1), copyObject(((Object* (*)(Object*))getMethodForCurrentType(p0, "size", NULL))(p0)));
   Object*(*next)(Object*) = getMethodForCurrentType(iterable, "next", NULL);
   Object*(*current)(Object*) = getMethodForCurrentType(iterable, "current", NULL);

   while(*(bool*)getAttributeValue(next(iterable), "value")) {
      v2 = current(iterable);

      return_obj = ifElseBlock0(v2, v1, v0, p0);
   }
   return return_obj;
}

Object* loopBlock0(Object* v0, Object* p0) {
   Object* return_obj = NULL;
   Object* v1 = NULL;
   Object* iterable = function_range(copyObject(createNumber(0)), copyObject(((Object* (*)(Object*))getMethodForCurrentType(p0, "size", NULL))(p0)));
   Object*(*next)(Object*) = getMethodForCurrentType(iterable, "next", NULL);
   Object*(*current)(Object*) = getMethodForCurrentType(iterable, "current", NULL);

   while(*(bool*)getAttributeValue(next(iterable), "value")) {
      v1 = current(iterable);

      return_obj = loopBlock1(v1, v0, p0);
   }
   return return_obj;
}

Object* function_Sort (Object* p0) {
   return letInNode0(p0);
}


int main() {
   srand(time(NULL));

   function_print(copyObject(function_Sort(copyObject(createVector(7, createNumber(78), createNumber(12), createNumber(100), createNumber(0), createNumber(6), createNumber(9), createNumber(4.5))))));
   return 0; 
}