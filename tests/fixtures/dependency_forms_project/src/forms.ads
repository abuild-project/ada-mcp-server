limited with Ada.Text_IO;
private with Ada.Strings;
limited private with Ada.Calendar;
generic
   with procedure Formal_Stop
     with No_Return;
package Forms is
   procedure Stop
     with Inline, No_Return;
   protected Guard is
      procedure Touch;
   end Guard;
end Forms;
