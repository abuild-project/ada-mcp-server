with Ada.Text_IO;
with Generic_Seed;
generic
   with -- The formal function is not the compilation unit.
     function Less (Left, Right : Integer) return Boolean;
   with procedure Touch (Value : Integer);
   with package Formal_Seed is new Generic_Seed (<>);
   type Callback_Function is access function return Boolean;
package Generic_Probe is
end Generic_Probe;
