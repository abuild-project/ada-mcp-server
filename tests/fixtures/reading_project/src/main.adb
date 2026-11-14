with Reading;
procedure Main is
   Item : Reading.Counter := (Value => 0);
   procedure Step is
   begin
      Reading.Reading_Probe_Increment (Item);
   end Step;
begin
   Step;
   -- No semantic target.
end Main;
