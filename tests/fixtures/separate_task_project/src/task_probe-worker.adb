with Ada.Text_IO;
separate (Task_Probe)
task body Worker is
   procedure Inner is
   begin
      Ada.Text_IO.Put_Line ("worker");
   end Inner;
begin
   Inner;
end Worker;
