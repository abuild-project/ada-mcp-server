with Reading;
procedure Main is
   -- Owned mutation moves semantic targets.

   Other : Reading.Alternate_Counter := (Value => 0);

   procedure Step is
   begin
      Other.Value := Other.Value + 1;
   end Step;
begin
   Step;
   -- No semantic target.
end Main;
