param(
    [string]$Path = ".",
    [int]$Depth = 999,
    [string[]]$IgnoreFolders = @(".git", "node_modules", "__pycache__", "test", "test_data"),
    [string[]]$IgnoreExtensions = @(".pyc", ".log", ".tmp")
)

$Path = (Resolve-Path $Path).Path

Write-Output (Split-Path $Path -Leaf)

function Show-Tree {
    param(
        [string]$Dir,
        [string]$Prefix = "",
        [int]$Level = 0
    )

    if ($Level -ge $Depth) {
        return
    }

    $dirs = Get-ChildItem $Dir -Directory |
        Where-Object { $_.Name -notin $IgnoreFolders } |
        Sort-Object Name

    $files = Get-ChildItem $Dir -File |
        Where-Object { $_.Extension -notin $IgnoreExtensions } |
        Sort-Object Name

    $items = @($dirs) + @($files)

    for ($i = 0; $i -lt $items.Count; $i++) {

        $item = $items[$i]
        $last = ($i -eq $items.Count - 1)

        if ($last) {
            $branch = "└── "
            $nextPrefix = $Prefix + "    "
        }
        else {
            $branch = "├── "
            $nextPrefix = $Prefix + "│   "
        }

        if ($item.PSIsContainer) {
            Write-Output "$Prefix$branch$($item.Name)\"
            Show-Tree $item.FullName $nextPrefix ($Level + 1)
        }
        else {
            Write-Output "$Prefix$branch$($item.Name)"
        }
    }
}

Show-Tree $Path