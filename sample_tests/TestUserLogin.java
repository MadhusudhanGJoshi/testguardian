import org.junit.Test;
import static org.junit.Assert.*;

public class TestUserLogin {
    @Test
    public void testValidLogin() {
        String result = UserService.login("admin", "password");
        assertEquals("success", result);
    }

    @Test
    public void testInvalidPassword() {
        String result = UserService.login("admin", "wrong");
        assertNotNull(result);
        assertEquals("failure", result);
    }
}
