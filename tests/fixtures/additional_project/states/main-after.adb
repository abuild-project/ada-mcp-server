with Probe;
procedure Main is
   -- This complete state is written only to an owned copy.

   Counter : Natural := 0;
begin
   Counter := Probe.Merge (1, 2, 3);
   Probe.Advance (Counter);
   Probe.Advance (Counter);
   -- No callable symbol here; Counter is only comment text.
end Main;
