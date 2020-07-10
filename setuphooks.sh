#!/bin/sh
if ! [ -d .git ]; then
	echo "$0 must be run from the directory containing .git"
	exit 1
fi
if ! [ -x scripts/git-pre-commit-hook ]; then
	echo "Cannot find scripts/git-pre-commit-hook"
	exit 1
fi
if [ -e .git/hooks/pre-commit ]; then
	echo ".git/hooks/pre-commit already exists; aborting"
	exit 1
fi
cat > .git/hooks/pre-commit.$$ <<'EOF'
#!/bin/sh
exec scripts/git-pre-commit-hook "$@"
EOF
chmod +x .git/hooks/pre-commit.$$
mv .git/hooks/pre-commit.$$ .git/hooks/pre-commit
