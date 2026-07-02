# 21. Merge Two Sorted Lists

## Metadata

- Created: 2026-07-02
- Next review: 2026-07-05

## My Attempt

```c
struct ListNode* mergeTwoLists(struct ListNode* list1, struct ListNode* list2) {
    struct ListNode dummy;
    dummy.next = NULL;
    struct ListNode* tail = &dummy;

    while (list1 != NULL && list2 != NULL) {
        if (list1->val <= list2->val) {
            tail->next = list1;
            list1 = list1->next;
        } else {
            tail->next = list2;
            list2 = list2->next;
        }
        tail = tail->next;
    }

    tail->next = (list1 != NULL) ? list1 : list2;
    return dummy.next;
}
```

## AI Review

### Verdict

The solution is correct and uses the standard iterative merge technique with two input pointers, a dummy node, and a tail pointer.

### Current Approach

Compare the current nodes of both lists and append the smaller one to the result. Once one list is exhausted, append the remaining part of the other list.

### Complexity Analysis

- Time complexity: `O(m + n)`
- Space complexity: `O(1)`

### Knowledge Card

- A dummy node removes special handling for the result head.
- A tail pointer keeps appending nodes efficient and clear.
- The process mirrors the merge step in merge sort.
- Reusing the original nodes keeps auxiliary space constant.

### Next-Time Reminder

For linked-list merge, insertion, or deletion problems, consider whether a dummy node can simplify edge cases.
