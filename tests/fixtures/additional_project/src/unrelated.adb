procedure Unrelated is
   Counter : Integer := 100;
   procedure Increment is
   begin
      Counter := Counter + 10;
   end Increment;
begin
   Increment;
end Unrelated;
