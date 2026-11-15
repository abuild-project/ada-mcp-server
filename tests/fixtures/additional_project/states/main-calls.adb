with Probe;
procedure Main is
   Counter : Integer := 0;
begin
   -- The Combine edge is removed without changing package sources.

   Probe.Increment (Counter);
   -- No callable symbol here; Counter is only comment text.
end Main;
