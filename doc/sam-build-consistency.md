# Ensuring Consistency Between Local and CI/CD AWS SAM Deployments

To avoid "works on my machine" issues and ensure reliable, reproducible deployments, follow these best practices for AWS SAM projects:

## 1. Use Container Builds Everywhere
- **Always use `sam build --use-container`** both locally and in CI/CD.
- This ensures dependencies are built in an environment identical to AWS Lambda, regardless of your local OS or Python version.

## 2. Unified Directory Structure
- Place your Lambda handler and `requirements.txt` together (e.g., `src/lambda/`).
- Set `CodeUri: src/lambda/` in your `template.yaml`.
- Do not manually create or manage a `build/` directory; let SAM manage `.aws-sam/`.

## 3. Unified Build and Deploy Commands
- **Local:**
  ```bash
  sam build --use-container
  sam deploy --guided
  ```
- **CI/CD (GitHub Actions):**
  ```yaml
  - name: Build and package Lambda
    run: sam build --use-container
  - name: Deploy with SAM
    run: sam deploy ...
  ```
- This guarantees the same process and output everywhere.

## 4. Ignore Build Artifacts
- Add `.aws-sam/` to your `.gitignore` to keep your repo clean.

## 5. No Manual Dependency Management
- Let SAM and the container build process handle all dependency packaging.
- Do not pre-bundle dependencies or copy files by hand.

## 6. Summary Table
| Step         | Local Dev         | CI/CD (GitHub Actions) | Parity? |
|--------------|-------------------|------------------------|---------|
| Build        | sam build --use-container | sam build --use-container | ✅      |
| Deploy       | sam deploy        | sam deploy             | ✅      |
| Artifacts    | .aws-sam/         | .aws-sam/              | ✅      |

## 7. Benefits
- Eliminates environment drift
- Simplifies troubleshooting
- Ensures production reliability

---

**Always use container builds and unified commands for AWS SAM projects.** 