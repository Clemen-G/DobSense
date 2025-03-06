use strict;
use warnings;
use Template;
use File::Basename;
use File::Spec::Functions qw(rel2abs);

my $script_dir = dirname(rel2abs($0));
my $template_path = "$script_dir/nginx.conf.tt";

my ($forward_to_nextjs, $dns_server) = @ARGV;
my %vars = (
    forward_to_nextjs => (lc($forward_to_nextjs) eq 'true'),
    dns_server => $dns_server,
);

my $template = Template->new({
    ABSOLUTE => 1,
});

$template->process($template_path, \%vars)
    || die "Template processing failed: ", $template->error();