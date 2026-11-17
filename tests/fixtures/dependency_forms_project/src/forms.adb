package body Forms is
   procedure Stop is
   begin
      raise Program_Error;
   end Stop;
   protected body Guard is separate;
end Forms;
