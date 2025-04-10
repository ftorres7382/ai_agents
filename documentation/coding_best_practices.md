# Coding Best Practices

1. Use the following format to divide the code into sections. 
    - This makes non collapsable sections of the code collapsable in VS code
    - Never add a newline afer region:
    - Never have a newline between the code and the end region
    - Always separate sections by two newlines
    ```python
        ##########################
        # Section name 1
        ##########################
        # region:
        {code}
        # endregion


        ##########################
        # Section name 2
        ##########################
        # region:
        {code}
        # endregion
    ```
1. Calculations and operations in the configurations files should be kept to a minimum
1. Never use """ for multiline strings. Always use ''' instead