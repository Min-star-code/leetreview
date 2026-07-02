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

### 代码结论

代码思路正确，使用了合并两个有序链表的标准迭代方法：双指针、哑节点和尾指针。

### 当前思路

每次比较两个链表当前节点的值，把较小节点连接到结果链表尾部。当一个链表遍历结束后，将另一个链表的剩余部分直接接上。

### 复杂度分析

- 时间复杂度：`O(m + n)`
- 空间复杂度：`O(1)`

### 知识点卡片

- 哑节点可以统一处理结果链表的头节点。
- 尾指针用于持续连接新节点。
- 该过程与归并排序中的 merge 步骤相同。
- 直接复用原链表节点可以保持常数额外空间。

### 下次提醒

遇到链表合并、插入或删除问题时，先考虑能否使用哑节点简化边界情况。

