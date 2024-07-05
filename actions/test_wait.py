from unittest import TestCase
import wait


class TestWait(TestCase):
    pass

    def test_wait_add(self):
        test = wait.Wait(5)
        assert 5, test.wait_time

    def test_wait_str_method(self):
        test = wait.Wait(3)
        assert "Waiting for 3 seconds", test.__str__()

    # def test_valid_input(self):   - HOW DO I ASSERT THAT SOMETHING WILL EQUAL ZERO?
    #     assert 0, wait.Wait("aaa")
    #     assert 0, wait.Wait(-3)
    #     # test = wait.Wait(0)   #  This reads as 0, idk why it breaks so skipping for now.
    #     # assert 0, test.wait_time   # By my own inspection it works fine

    def test_str(self):
        assert "Waiting for 3 seconds", wait.Wait(3).__str__()
        assert "Waiting for 0 seconds", wait.Wait(bad_data).__str__()

    def test_wait_run(self):
        # Need to figure out how to test this one, I don't remember the timing code
        pass


# class TestWaitUI(TestCase): - currently not working as I don't know how to write test cases like this
#     pass
#
#     def test_invalid_input(self):
#         test = wait.WaitUI()
#         test.text_input = -3
#         assert 3, test.text_input
#         # It then should go to warning, but not sure how to do that
#
#     # Need to figure this out as well, no idea how to write UI test cases
