# 协作开发工作流规范

本文档为 `RL_PCB` 项目的双人协作开发提供了一套标准的 Git 工作流。遵循此规范有助于保持代码库的整洁、减少合并冲突，并确保主分支的稳定性。

## 核心原则

1.  **`main` 分支是神圣的**: `main` 分支应始终保持稳定、可运行的状态。任何时候的代码都应该是可部署/可交付的。
2.  **禁止直接推送到 `main`**: 任何人都不能直接向 `main` 分支 `push` 代码。所有代码变更必须通过 `Pull Request` (PR) 的方式合入。
3.  **Feature Branch 工作流**: 每项新功能、错误修复或任何独立的开发任务都应该在一个新的、独立的 "feature" 分支上进行。

---

## 详细开发流程
refac
### 1. 开始新任务：同步并创建新分支

在开始任何新的开发任务之前，请确保你的 `main` 分支是最新的，然后从 `main` 分支创建你的工作分支。

```bash
# 1. 切换到 main 分支
git checkout main

# 2. 从远程仓库拉取最新的 main 分支代码
git pull origin main

# 3. 基于最新的 main 分支，创建并切换到一个新的 feature 分支
# 分支命名建议: <你的名字>/<功能简述>
# 例如: zhangsan/add-user-login 或 lisi/fix-display-bug
git checkout -b your-name/feature-description
```

### 2. 开发与提交

在新创建的分支上进行代码的修改和开发。

*   **频繁提交**: 养成频繁提交代码的习惯。每次提交都应该是一个逻辑上完整的、小规模的变更。
*   **写好 Commit Message**: 提交信息应清晰、有意义，能概括本次提交的内容。
    *   **推荐格式**: `type: subject` (e.g., `feat: Add user login API`, `fix: Correct calculation error in reward function`)
    *   `type`可以是：`feat` (新功能), `fix` (修复bug), `docs` (文档), `style` (格式), `refactor` (重构), `test` (测试) 等。

```bash
# 添加你的修改
git add .

# 提交你的修改
git commit -m "feat: Add initial implementation for data loading"

# ... 继续开发和提交 ...
```

### 3. 保持分支与 `main` 同步

在你的开发过程中，另一位开发者可能已经将他们的代码合并到了 `main` 分支。为了避免未来合并时出现大的冲突，你应该定期将 `main` 分支的最新变更同步到你的 feature 分支。推荐使用 `rebase` 来保持提交历史的整洁。

```bash
# 1. 获取远程 main 分支的最新更新 (但还不应用)
git fetch origin main

# 2. 将你的当前分支 rebase 到最新的 main 分支上
# 这会把你的提交“重放”在 main 分支最新代码的顶端
git rebase origin/main
```

**处理冲突**: 如果 `rebase` 过程中出现冲突，Git 会暂停并让你解决。解决完冲突后，使用 `git add .` 将修改后的文件标记为已解决，然后运行 `git rebase --continue` 继续。如果想中止 `rebase`，可以运行 `git rebase --abort`。

### 4. 推送并创建 Pull Request (PR)

当你的功能开发完成，并且已经与 `main` 分支同步后，就可以将你的分支推送到远程仓库，并创建一个 Pull Request。

```bash
# 推送你的 feature 分支到远程仓库
git push origin your-name/feature-description
```

推送后，打开 GitHub 上的项目页面，你会看到一个提示，引导你为刚推送的分支创建一个 Pull Request。

*   **目标分支** 应设置为 `main`。
*   **标题和描述**: 为 PR 写一个清晰的标题和详细的描述。说明你做了什么、为什么这么做、以及（如果可能的话）如何测试。
*   **Reviewer**: 在 PR 中指定另一位开发者作为 `Reviewer` (审查者)。

### 5. 代码审查 (Code Review)

代码审查是保证代码质量的关键环节。

*   **审查者**: 另一位开发者会审查你的代码，检查逻辑、风格、潜在问题等，并在 PR 页面上提出评论或修改建议。
*   **作者**: 根据审查意见进行修改。直接在你本地的 feature 分支上修改并提交，然后再次推送到远程。PR 会自动更新。

这个过程可能会往复几次，直到审查者对代码满意为止。

### 6. 合并 Pull Request

当 PR 被审查者 `Approve` (批准) 后，就可以将其合并到 `main` 分支了。

*   **推荐使用 "Squash and Merge"**: 在 GitHub 的合并按钮上，选择 "Squash and Merge"。这会将你的 feature 分支上的所有提交合并成一个单一的、完整的提交，然后再合入 `main` 分支。这能让 `main` 分支的提交历史非常干净、清晰。

### 7. 删除已合并的分支

PR 合并后，你的 feature 分支就完成了它的使命。可以将其删除，以保持仓库的整洁。

*   GitHub 在合并 PR 后通常会提供一个按钮，让你方便地删除远程分支。
*   你也可以在本地删除这个分支：
    ```bash
    # 切换回 main 分支
    git checkout main

    # 删除本地的 feature 分支
    git branch -d your-name/feature-description
    ```

---

## 总结：一次完整的流程

1.  `git checkout main`
2.  `git pull origin main`
3.  `git checkout -b zhangsan/my-new-feature`
4.  *(...写代码...)*
5.  `git add .` & `git commit -m "..."`
6.  `git fetch origin main` & `git rebase origin/main` *(可选，但推荐)*
7.  `git push origin zhangsan/my-new-feature`
8.  在 GitHub 上创建 PR (zhangsan/my-new-feature -> main)，并指定 Reviewer。
9.  *(...代码审查和修改...)*
10. Reviewer 批准后，在 GitHub 上使用 "Squash and Merge" 合并 PR。
11. 删除 feature 分支。
12. 另一位开发者 `git pull origin main` 开始新的循环。 