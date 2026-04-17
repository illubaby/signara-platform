Summary: what problem you hit
Your git push over HTTPS was failing with 403 Forbidden even after you authenticated (password/browser login succeeded).
The key clue is that the response didn’t come “directly from GitHub”; it was coming from your corporate proxy: Zscaler (Server: Zscaler/0.0).
So this was not a local Windows/admin permission issue. It was a network policy blocking the specific GitHub push endpoint (git-receive-pack) over HTTPS.
How it was solved
Switched the repo from HTTPS push to SSH so the push traffic avoids the blocked HTTPS path.
Configured SSH to go through port 443 (since many corporate networks only allow 443 outbound), by setting in your SSH config:
'''
Host github.com
    HostName ssh.github.com
    Port 443
    User git
    IdentityFile ~/.ssh/id_rsa
    IdentitiesOnly yes
'''
Then you used the SSH remote (git@github.com:...) and git push worked because it no longer relied on the blocked HTTPS git-receive-pack request.
Why authentication “looked successful” but still failed
HTTPS auth can succeed, but the proxy can still deny the upload operation (push) by policy.
That’s why it kept asking for credentials / showing you logged in, yet push was still rejected.