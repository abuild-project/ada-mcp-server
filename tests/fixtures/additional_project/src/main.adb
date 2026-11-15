with Probe;
procedure Main is
   Counter : Integer := 0;
begin
   Counter := Probe.Combine (1, 2);
   Probe.Increment (Counter);
   -- No callable symbol here; Counter is only comment text.
end Main;
